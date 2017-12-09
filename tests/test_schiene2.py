#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `schiene2` package."""

import pytest
import pendulum


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


class TestDataStructure:
    def test_connection_consists_of_multiple_trips(self, connection):
        assert hasattr(connection, 'journeys')
        assert all([isinstance(journey, Journey) for journey in connection.journeys])

    def test_trip_has_departure_and_arrival_properties(self, journey):
        assert isinstance(journey.departure, DepartureOrArrival)
        assert isinstance(journey.arrival, DepartureOrArrival)

    def test_journey_has_a_train_associated(self, journey):
        assert isinstance(journey.train, Train)

    def test_departure_or_arrival_has_station_time_track(self, departure):
        assert isinstance(departure.station, Station)
        assert hasattr(departure, 'time')
        assert hasattr(departure, 'track')
