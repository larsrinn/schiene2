from pendulum import Pendulum


class Connection:
    def __init__(self, journeys):
        self.journeys = journeys

    @classmethod
    def search(cls, departure, arrival, time):
        raise NotImplementedError
        return cls([])


class Station:
    def __init__(self, name):
        self.name = name


class Train:
    def __init__(self, number):
        self.number = number


class DepartureOrArrival:
    def __init__(self, station: Station, time: Pendulum, track):
        self.station = station
        self.time = time
        self.track = track


class Journey:
    def __init__(self, departure: DepartureOrArrival, arrival: DepartureOrArrival, train: Train):
        self.departure = departure
        self.arrival = arrival
        self.train = train
