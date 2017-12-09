import pytest
import pendulum

from schiene2.models import Connection, DepartureOrArrival, Train, Station, Journey

def test_can_create_by_search():
    connection = Connection.search(
        'Frankfurt Hbf',
        'Hinterzarten',
        pendulum.create(2017, 12, 9, 14, 57)
    )
    assert isinstance(connection, Connection)


class TestDepartureOrArrival:
    def test_can_create_from_dict(self):
        dct = {
            'station': 'Frankfurt Hbf',
            'time': pendulum.create(2017, 12, 9, 14, 57),
            'track': 6
        }
        doa = DepartureOrArrival.from_dict(dct)
        assert isinstance(doa, DepartureOrArrival)
        assert isinstance(doa.station, Station)


class TestTrain:
    def test_can_create_from_dict(self):
        dct = {
            'number': 'ICE 293'
        }
        train = Train.from_dict(dct)
        assert isinstance(train, Train)


class TestJourney:
    def test_can_create_from_dict(self):
        dct = {
            'departure': {
                'station': 'Frankfurt Hbf',
                'time': pendulum.create(2017, 12, 9, 14, 57),
                'track': 6
            },
            'arrival': {
                'station': 'Freiburg Hbf',
                'time': pendulum.create(2017, 12, 9, 17, 5),
                'track': 4
            },
            'train': {
                'number': 'ICE 293'
            }
        }
        journey = Journey.from_dict(dct)
        #todo check if correct data is assigned
        assert isinstance(journey, Journey)
        assert isinstance(journey.departure, DepartureOrArrival)
        assert isinstance(journey.arrival, DepartureOrArrival)
        assert isinstance(journey.train, Train)


class TestConnection:
    def test_can_create_from_list(self):
        lst = [
            {
                'departure': {
                    'station': 'Frankfurt Hbf',
                    'time': pendulum.create(2017, 12, 9, 14, 57),
                    'track': 6
                },
                'arrival': {
                    'station': 'Freiburg Hbf',
                    'time': pendulum.create(2017, 12, 9, 17, 5),
                    'track': 4
                },
                'train': {
                    'number': 'ICE 293'
                }
            },
            {
                'departure': {
                    'station': 'Freiburg Hbf',
                    'time': pendulum.create(2017, 12, 9, 17, 22),
                    'track': 8
                },
                'arrival': {
                    'station': 'Waldkirch',
                    'time': pendulum.create(2017, 12, 9, 17, 56),
                    'track': 1
                },
                'train': {
                    'number': 'ICE 293'
                }
            }
        ]
        connection = Connection.from_list(lst)
        assert isinstance(connection, Connection)
        assert len(connection.journeys) == 2
        assert all([isinstance(journey, Journey) for journey in connection.journeys])
