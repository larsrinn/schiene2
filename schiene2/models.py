import pendulum
from pendulum import Pendulum
from schiene2.mobile_page import DetailParser, connections


class Connection:
    def __init__(self, journeys):
        self.journeys = journeys

    def __str__(self):
        return '{}: {} -> {}'.format(
            self.origin.time,
            self.origin.station.name,
            self.destination.station.name
        )

    @classmethod
    def search(cls, origin, destination, time=pendulum.now()):
        url = connections(origin, destination, time)[0]['detail_url']
        parser = DetailParser(url)
        return cls.from_list(parser.journeys())

    @classmethod
    def from_list(cls, lst):
        journeys = [
            Journey.from_dict(_) for _ in lst
        ]
        return Connection(journeys)

    @property
    def origin(self):
        return self.journeys[0].departure

    @property
    def destination(self):
        return self.journeys[-1].arrival


class Station:
    def __init__(self, name):
        self.name = name


class Train:
    def __init__(self, number):
        self.number = number

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


class DepartureOrArrival:
    def __init__(self, station: Station, time: Pendulum, track):
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
