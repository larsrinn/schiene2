import pendulum
import pytest
from schiene2.models import Connection, Station, Train, DepartureOrArrival, Journey


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
    return Connection(journeys=[journey])
