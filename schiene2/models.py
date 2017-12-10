import pendulum
from pendulum import Pendulum
from schiene2.mobile_page import DetailParser, scrape_connections, ConnectionListParser


class Station:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class BaseConnection:
    def __str__(self):
        return '\n{}: {}\n-> {}: {}'.format(
            self.origin.time.strftime('%H:%M'),
            self.origin.station.name,
            self.destination.time.strftime('%H:%M'),
            self.destination.station.name
        )

    def __repr__(self):
        return self.__str__()

    def get_details(self):
        raise NotImplementedError


class ConnectionDetails(BaseConnection):
    def __init__(self, journeys):
        self.journeys = journeys
        self._original_journeys = None

    @property
    def original_journeys(self):
        return self._original_journeys or self.journeys

    @original_journeys.setter
    def original_journeys(self, value):
        if self._original_journeys is None:
            self._original_journeys = value

    @classmethod
    def search(cls, origin, destination, time=pendulum.now()):
        origin = str(origin)
        destination = str(destination)
        url = scrape_connections(origin, destination, time)[0]['detail_url']
        parser = DetailParser(url)
        return cls.from_list(parser.journeys())

    @classmethod
    def from_list(cls, lst):
        journeys = [
            Journey.from_dict(_) for _ in lst
        ]
        return ConnectionDetails(journeys)

    def update_details(self):
        pass

    def search_after_missed_at_station(self, station: Station):
        first_missed_journey = [journey
                                for journey in self.journeys
                                if journey.departure.station == station][0]
        earliest_departure_time = first_missed_journey.departure.time.add(minutes=1)
        return self.__class__.search(
            origin=station,
            destination=self.destination.station,
            time=earliest_departure_time
        )

    def update_after_station(self, station: Station, new_part_connection):
        self.original_journeys = self.journeys[:]
        start_index_original_journeys = self.transition_stations.index(station) + 1
        del self.journeys[start_index_original_journeys:]
        self.journeys += new_part_connection.journeys

    @property
    def origin(self):
        return self.journeys[0].departure

    @property
    def destination(self):
        return self.journeys[-1].arrival

    @property
    def transition_stations(self):
        return [journey.departure.station for journey in self.journeys[1:]]

    @property
    def delay_at_destination(self):
        period = self.destination.time - self.original_journeys[-1].arrival.time
        return period.as_timedelta()

    @property
    def transfers(self):
        return len(self.journeys) - 1

    def get_details(self):
        return self


class Connection(BaseConnection):
    #todo test data structure
    def __init__(self, detail_url, origin, destination, transfers):
        self.detail_url = detail_url
        self.origin = origin
        self.destination = destination
        self.transfers = transfers

    def get_details(self):
        #todo test
        parser = DetailParser(self.detail_url)
        return ConnectionDetails.from_list(parser.journeys())


class ConnectionList:
    # TODO test data structure
    def __init__(self, connections):
        self.connections = connections

    def __str__(self):
        return self.connections.__str__()

    def __repr__(self):
        return self.connections.__repr__()

    @classmethod
    def search(cls, origin, destination, time=pendulum.now(), only_direct=False):
        #todo test
        parser = ConnectionListParser(origin, destination, time, only_direct)
        return cls.from_list(parser.connections)

    @classmethod
    def from_list(cls, lst):
        #TODO test
        connections = [
            Connection(
                detail_url=connection['detail_url'],
                origin=DepartureOrArrival.from_dict(connection['origin']),
                destination=DepartureOrArrival.from_dict(connection['destination']),
                transfers=connection['transfers']
            )
            for connection in lst
        ]
        return cls(connections)


class Train:
    def __init__(self, number):
        self.number = number

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


class DepartureOrArrival:
    def __init__(self, station: Station, time: Pendulum, track=None):
        self.station = station
        self.time = time
        self.track = track

    @classmethod
    def from_dict(cls, dct):
        dct['station'] = Station(dct['station'])
        return DepartureOrArrival(**dct)


class Journey:
    def __init__(self, departure: DepartureOrArrival, arrival: DepartureOrArrival, train: Train):
        self.departure = departure
        self.arrival = arrival
        self.train = train

    @classmethod
    def from_dict(cls, dct):
        return cls(
            departure=DepartureOrArrival.from_dict(dct['departure']),
            arrival=DepartureOrArrival.from_dict(dct['arrival']),
            train=Train.from_dict(dct['train'])
        )
