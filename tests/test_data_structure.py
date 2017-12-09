#!/usr/bin/env python
# -*- coding: utf-8 -*-

from schiene2.models import Station, Train, DepartureOrArrival, Journey


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
