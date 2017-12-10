import pytest
import pendulum

from schiene2.models import ConnectionDetails, DepartureOrArrival, Train, Station, Journey


@pytest.fixture
def updated_connection(complete_connection, new_part_connection):
    station = complete_connection.transition_stations[0]
    complete_connection.update_after_station(station, new_part_connection)
    return complete_connection


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

    def test_delay(self, arrival):
        arrival.actual_time = arrival.time.add(minutes=5)
        assert arrival.delay == pendulum.interval(minutes=5)


class TestTrain:
    def test_can_create_from_dict(self):
        dct = {
            'number': 'ICE 293'
        }
        train = Train.from_dict(dct)
        assert isinstance(train, Train)


class TestStation:
    def test_two_stations_are_equal_if_names_are_identical(self):
        station1 = Station('Freiburg Hbf')
        station2 = Station('Freiburg Hbf')
        assert station1 == station2

        station3 = Station('Freiburg')
        assert station1 != station3


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
        # todo check if correct data is assigned
        assert isinstance(journey, Journey)
        assert isinstance(journey.departure, DepartureOrArrival)
        assert isinstance(journey.arrival, DepartureOrArrival)
        assert isinstance(journey.train, Train)


class TestConnectionDetails:
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
                    'number': 'RE 235'
                }
            }
        ]
        connection = ConnectionDetails.from_list(lst)
        assert isinstance(connection, ConnectionDetails)
        assert len(connection.journeys) == 2
        assert all([isinstance(journey, Journey) for journey in connection.journeys])

    def test_can_create_by_search(self):
        connection = ConnectionDetails.search(
            'Frankfurt Hbf',
            'Hinterzarten',
            pendulum.create(2017, 12, 9, 14, 57)
        )
        assert isinstance(connection, ConnectionDetails)

    def test_search_can_be_invoked_with_stations(self):
        connection = ConnectionDetails.search(
            Station('Frankfurt Hbf'),
            Station('Hinterzarten'),
            pendulum.create(2017, 12, 9, 14, 57)
        )
        assert isinstance(connection, ConnectionDetails)

    def test_can_access_origin_and_destination(self, complete_connection):
        assert complete_connection.origin.station.name == 'Köln Hbf'
        assert complete_connection.destination.station.name == 'Hinterzarten'

    def test_can_access_transition_stations(self, complete_connection):
        transition_stations = complete_connection.transition_stations
        assert transition_stations == [Station('Frankfurt Hbf'), Station('Freiburg Hbf')]

    def test_can_search_for_part_connection_after_train_missed(self, complete_connection, mocker):
        station = complete_connection.transition_stations[0]
        mock_search = mocker.patch('schiene2.models.ConnectionDetails.search')

        complete_connection.search_after_missed_at_station(station)

        call_kwargs = mock_search.call_args[1]
        assert call_kwargs['origin'] == station
        assert call_kwargs['destination'] == complete_connection.destination.station
        assert call_kwargs['time'] > complete_connection.journeys[1].departure.time

    def test_can_update_after_train_missed(self, complete_connection, new_part_connection):
        original_journeys = complete_connection.journeys[:]
        station = complete_connection.transition_stations[0]

        complete_connection.update_after_station(station, new_part_connection)

        assert complete_connection.journeys[-2:] == new_part_connection.journeys[-2:]
        assert original_journeys[:1] == complete_connection.journeys[:1]

    def test_can_access_original_journeys_after_update(self, complete_connection, new_part_connection):
        original_journeys = complete_connection.journeys[:]
        station = complete_connection.transition_stations[0]

        complete_connection.update_after_station(station, new_part_connection)

        assert complete_connection.original_journeys == original_journeys

    def test_update_twice(self, complete_connection, new_part_connection, new_part_connection2):
        original_journeys = complete_connection.journeys[:]

        complete_connection.update_after_station(
            complete_connection.transition_stations[0],
            new_part_connection
        )
        complete_connection.update_after_station(
            complete_connection.transition_stations[1],
            new_part_connection2
        )

        expected_journeys = [
            original_journeys[0],
            new_part_connection.journeys[0],
            new_part_connection2.journeys[0]
        ]
        assert complete_connection.journeys == expected_journeys
        assert complete_connection.original_journeys == original_journeys

    def test_can_access_total_delay_if_connections_missed(self, updated_connection):
        assert updated_connection.delay_at_destination == pendulum.interval(minutes=63)

    def test_delay_is_zero_if_no_journey_missed(self, complete_connection):
        assert complete_connection.delay_at_destination == pendulum.interval(minutes=4)

    def test_number_of_transfers(self, complete_connection):
        assert complete_connection.transfers == 2


class TestConnectionList:
    def test_can_search_on_mobile_page(self):
        pass
