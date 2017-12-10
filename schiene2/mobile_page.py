from bs4 import BeautifulSoup
import pendulum
import requests
import re


def scrape_connections(origin, destination, dt=pendulum.now(), only_direct=False):
    # todo remove this, when adopted logic in connectiondtail after missed at station
    """
    Find connections between two stations

    Args:
        origin (str): origin station
        destination (str): destination station
        dt (datetime): date and time for query
        only_direct (bool): only direct connections
    """
    query = {
        'S': origin,
        'Z': destination,
        'date': dt.strftime("%d.%m.%y"),
        'time': dt.strftime("%H:%M"),
        'start': 1,
        'REQ0JourneyProduct_opt0': 1 if only_direct else 0
    }
    rsp = requests.get('http://mobile.bahn.de/bin/mobil/query.exe/dox?', params=query)
    return parse_connections(rsp.text)


def parse_connections(html):
    if 'Ihre Eingabe ist nicht eindeutig' in html:
        html = handle_ambiguous_entry(html)
    soup = BeautifulSoup(html, "html.parser")
    connections = list()

    for row in soup.find_all("td", class_="overview timelink"):
        columns = row.parent.find_all("td")

        data = {
            'detail_url': columns[0].a.get('href'),
            'departure': columns[0].a.contents[0].string,
            'arrival': columns[0].a.contents[2].string,
            'transfers': int(columns[2].contents[0]),
            'time': columns[2].contents[2],
            'products': columns[3].contents[0].split(', '),
        }

        if columns[1].find('img'):
            data['canceled'] = True
        elif columns[1].find('span', class_="okmsg"):
            data['ontime'] = True
        elif columns[1].find('span', class_="red"):
            if hasattr(columns[1].contents[0], 'text'):
                delay_departure = columns[1].contents[0].text.replace("ca. +", "")
            else:
                delay_departure = 0
            if hasattr(columns[1].contents[2], 'text'):
                delay_arrival = columns[1].contents[2].text.replace("ca. +", "")
            else:
                delay_arrival = 0
            data['delay'] = {
                'delay_departure': int(delay_departure),
                'delay_arrival': int(delay_arrival)
            }
        connections.append(data)
    return connections


def handle_ambiguous_entry(html):
    return html


class ConnectionListParser:
    def __init__(self, origin, destination, dt=pendulum.now(), only_direct=False):
        query = {
            'S': str(origin),
            'Z': str(destination),
            'date': dt.strftime("%d.%m.%y"),
            'time': dt.strftime("%H:%M"),
            'start': 1,
            'REQ0JourneyProduct_opt0': 1 if only_direct else 0
        }
        rsp = requests.get('http://mobile.bahn.de/bin/mobil/query.exe/dox?', params=query)
        html = rsp.text
        if 'Ihre Eingabe ist nicht eindeutig' in html:
            html = self.handle_ambiguous_entry(html)
        self.soup = BeautifulSoup(html, 'html.parser')

    @property
    def connections(self):
        connections = []
        for connection_row in self.connection_rows:
            columns = connection_row.find_all("td")
            data = {
                'detail_url': columns[0].a.get('href'),
                'transfers': int(columns[2].contents[0]),
                'products': columns[3].contents[0].split(', '),
                'origin': {
                    'station': self.origin_station,
                    'time': self.timestring_to_pendulum(
                        columns[0].a.contents[0].string
                    ),
                },
                'destination': {
                    'station': self.destination_station,
                    'time': self.timestring_to_pendulum(
                        columns[0].a.contents[2].string
                    ),
                }
            }
            connections.append(data)
        return connections

    @property
    def connection_rows(self):
        return [first_column.parent
                for first_column
                in self.soup.find_all("td", class_="overview timelink")]

    def timestring_to_pendulum(self, timestring):
        datetimestring = "{} {}".format(self.datestring, timestring)
        return pendulum.parse(datetimestring, year_first=False, day_first=True, tz='Europe/Berlin')

    @staticmethod
    def handle_ambiguous_entry(html):
        soup = BeautifulSoup(html, 'html.parser')

        skip = [
            'chgBC=y&getstop',
            'advancedProductMode',
            'resetLocation=Z&dummy',
            'REQ0HafasSearchForw'
        ]
        field_values = {}
        for field in soup.find_all('input'):
            name = field.get('name')
            if name not in skip:
                field_values[name] = field.get('value')
        for field in soup.find_all('select'):
            name = field.get('name')
            first_option = field.find('option')
            field_values[name] = first_option.get('value')
        url = soup.find('form').get('action')

        response = requests.post(url, field_values)
        return response.text

    @property
    def header(self):
        return self.soup.find('div', class_='editBtnCon')

    @property
    def datestring(self):
        div_with_datestring = self.header.find('span', class_='grey')
        return re.search(r'\d\d.\d\d.\d\d\d\d', str(div_with_datestring)).group(0)

    @property
    def origin_station(self):
        return self.header.find_all('span')[0].string

    @property
    def destination_station(self):
        return self.header.find_all('span')[1].string


class DetailParser:
    def __init__(self, url):
        self.station_names = []
        self.times = []
        self.tracks = []
        rsp = requests.get(url)
        self.soup = BeautifulSoup(rsp.text, 'html.parser')

    def journeys(self):
        departure_or_arrivals = [
            self.convert_raw_departure_or_arrival(_) for _ in self._raw_departure_or_arrivals
        ]
        departures = departure_or_arrivals[::2]
        arrivals = departure_or_arrivals[1::2]
        journeys = []
        for departure, arrival, train in zip(departures, arrivals, self.trains):
            journeys.append({
                'departure': departure,
                'arrival': arrival,
                'train': train
            })
        return journeys

    @property
    def trains(self):
        trains = []
        for div in self.soup.find_all('div', class_='motSection'):
            div_with_train_number = div.find('span', class_='bold')
            number = re.search(r'\w+\s*\d+', str(div_with_train_number)).group(0)
            trains.append(dict(number=number))
        return trains

    @property
    def _raw_departure_or_arrivals(self):
        raw = self.soup.find_all('div', class_=['routeStart', 'routeChange', 'routeEnd'])
        return [_ for _ in raw if _.text != '\n']

    @property
    def datestring(self):
        div_with_datestring = self.soup.find('span', class_='querysummary2')
        return re.search(r'\d\d.\d\d.\d\d', str(div_with_datestring)).group(0)

    def convert_raw_departure_or_arrival(self, div):
        timestring = re.search(r'\d\d:\d\d', str(div)).group(0)
        datetimestring = "{} {}".format(self.datestring, timestring)
        datetime = pendulum.parse(datetimestring, year_first=False, day_first=True, tz='Europe/Berlin')
        try:
            track = re.search('Gl\. (\d+)', str(div)).group(1)
        except AttributeError:
            track = None
        return {
            'station': div.find('span', class_='bold').contents[0],
            'time': datetime,
            'track': track
        }
