from betamax import Betamax
import pendulum
import pytest
from schiene2.models import ConnectionDetails, Station, Train, DepartureOrArrival, Journey


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['record_mode'] = 'once'


@pytest.fixture
def train():
    return Train(number='ICE 329')


@pytest.fixture
def station():
    return Station(name='Freiburg Hbf')


@pytest.fixture
def departure(station):
    return DepartureOrArrival(station=station, time=pendulum.now(), track=2)


@pytest.fixture
def arrival():
    return DepartureOrArrival(station=station, time=pendulum.now().add(hours=1), track=6)


@pytest.fixture
def journey(departure, arrival, train):
    return Journey(departure, arrival, train)


@pytest.fixture
def connection(journey):
    return ConnectionDetails(journeys=[journey])


@pytest.fixture
def complete_connection():
    return ConnectionDetails([
        Journey(
            DepartureOrArrival(
                Station('Köln Hbf'),
                pendulum.create(2017, 12, 9, 13, 11),
                1,
                pendulum.create(2017, 12, 9, 13, 11),
            ),
            DepartureOrArrival(
                Station('Frankfurt Hbf'),
                pendulum.create(2017, 12, 9, 14, 22),
                18,
                pendulum.create(2017, 12, 9, 13, 11),
            ),
            Train(number='ICE 293')
        ),
        Journey(
            DepartureOrArrival(
                Station('Frankfurt Hbf'),
                pendulum.create(2017, 12, 9, 14, 45),
                6,
                pendulum.create(2017, 12, 9, 14, 45),
            ),
            DepartureOrArrival(
                Station('Freiburg Hbf'),
                pendulum.create(2017, 12, 9, 16, 45),
                3,
                pendulum.create(2017, 12, 9, 16, 45),
            ),
            Train(number='ICE 293')
        ),
        Journey(
            DepartureOrArrival(
                Station('Freiburg Hbf'),
                pendulum.create(2017, 12, 9, 17, 10),
                8,
                pendulum.create(2017, 12, 9, 17, 10),
            ),
            DepartureOrArrival(
                Station('Hinterzarten'),
                pendulum.create(2017, 12, 9, 17, 55),
                1,
                pendulum.create(2017, 12, 9, 17, 59),
            ),
            Train(number='RE 123')
        ),
    ])


@pytest.fixture
def new_part_connection():
    return ConnectionDetails.from_list([
        {
            'departure': {
                'station': 'Frankfurt Hbf',
                'time': pendulum.create(2017, 12, 9, 15, 45),
                'track': 8,
                'actual_time': pendulum.create(2017, 12, 9, 15, 45),
            },
            'arrival': {
                'station': 'Freiburg Hbf',
                'time': pendulum.create(2017, 12, 9, 17, 45),
                'track': 1,
                'actual_time': pendulum.create(2017, 12, 9, 17, 45),
            },
            'train': {
                'number': 'RE 236'
            }
        },
        {
            'departure': {
                'station': 'Freiburg Hbf',
                'time': pendulum.create(2017, 12, 9, 18, 22),
                'track': 8,
            },
            'arrival': {
                'station': 'Hinterzarten',
                'time': pendulum.create(2017, 12, 9, 18, 58),
                'track': 1
            },
            'train': {
                'number': 'RE 236'
            }
        },
    ])


@pytest.fixture
def new_part_connection2():
    return ConnectionDetails.from_list([
        {
            'departure': {
                'station': 'Freiburg Hbf',
                'time': pendulum.create(2017, 12, 9, 19, 22),
                'track': 8
            },
            'arrival': {
                'station': 'Hinterzarten',
                'time': pendulum.create(2017, 12, 9, 19, 56),
                'track': 1
            },
            'train': {
                'number': 'RE 238'
            }
        },
    ])
