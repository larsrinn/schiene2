import pendulum
import pytest
import requests

from unittest.mock import MagicMock

from _pytest.monkeypatch import MonkeyPatch

from schiene2.mobile_page import ConnectionListParser, ConnectionRowParser
from schiene2 import mobile_page
from betamax import Betamax


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['record_mode'] = 'once'


@pytest.fixture(scope='class')
def betamax_class_session(request):
    session = requests.Session()
    recorder = Betamax(session)
    with recorder.use_cassette(
        request.module.__name__ + '.' + request.cls.__name__
    ) as cassette:
        yield session


@pytest.fixture(scope='class')
def parser_recording(betamax_class_session):
    mp = MonkeyPatch()
    mp.setattr(mobile_page, 'requests', betamax_class_session)
    yield
    mp.undo()


@pytest.fixture(scope='class')
def recorded_parser(parser_recording):
    origin = 'Gießen Hbf'
    destination = 'Waldkirch'
    datetime = pendulum.create(2017, 12, 15, 14, 2, tz='Europe/Berlin')
    return ConnectionListParser(origin, destination, datetime)


class MockResponse(MagicMock):
    def __init__(self, **kwargs):
        super(MockResponse, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockHttpMethod(MagicMock):
    def __init__(self, **kwargs):
        super(MockHttpMethod, self).__init__()
        self.return_value = MockResponse(text='<html></html>', **kwargs)


class MockRequest(MagicMock):
    def __init__(self, **kwargs):
        super(MockRequest, self).__init__()
        self.get = kwargs.get('get') or MockHttpMethod()


@pytest.fixture
def mocked_request(monkeypatch):
    from schiene2 import mobile_page
    mocked_request = MockRequest()
    monkeypatch.setattr(mobile_page, 'requests', mocked_request)
    return mocked_request


class TestConnectionListParser:
    def test_init_requests_correct_page_and_arguments(self, mocked_request):
        ConnectionListParser('Gießen Hbf', 'Waldkirch')
        call_kwargs = mocked_request.get.call_args[1]
        assert call_kwargs['url'] == 'http://mobile.bahn.de/bin/mobil/query.exe/dox?'

    def test_init_requests_with_correct_params(self, mocked_request):
        time = pendulum.create(2017, 12, 13, 12, 00)
        ConnectionListParser('Gießen Hbf', 'Waldkirch', time)
        call_kwargs = mocked_request.get.call_args[1]
        assert call_kwargs['params'] == {
            'S': 'Gießen Hbf',
            'Z': 'Waldkirch',
            'date': '13.12.17',
            'time': '12:00',
            'start': 1,
            'REQ0JourneyProduct_opt0': 0
        }

    def test_connection_property(self, recorded_parser):
        connections = recorded_parser.connections
        for connection in connections:
            del connection['detail_url']  # detail_url is different in each request, can't parse from page
        assert connections == [
            {
                'transfers': 2,
                'products': ['IC', 'ICE', 'BSB'],
                'origin': {
                    'station': 'Gießen',
                    'time': pendulum.create(2017, 12, 15, 14, 22, tz='Europe/Berlin')
                },
                'destination': {
                    'station': 'Waldkirch',
                    'time': pendulum.create(2017, 12, 15, 18, 28, tz='Europe/Berlin')
                },

            },
            {
                'transfers': 3,
                'products': ['RE', 'ICE', 'BSB'],
                'origin': {
                    'station': 'Gießen',
                    'time': pendulum.create(2017, 12, 15, 14, 54, tz='Europe/Berlin')
                },
                'destination': {
                    'station': 'Waldkirch',
                    'time': pendulum.create(2017, 12, 15, 18, 28, tz='Europe/Berlin')
                },

            },
            {
                'transfers': 2,
                'products': ['RE', 'ICE', 'BSB'],
                'origin': {
                    'station': 'Gießen',
                    'time': pendulum.create(2017, 12, 15, 14, 54, tz='Europe/Berlin')
                },
                'destination': {
                    'station': 'Waldkirch',
                    'time': pendulum.create(2017, 12, 15, 19, 0, tz='Europe/Berlin')
                },

            },
        ]

    def test_datestring(self, recorded_parser):
        assert recorded_parser.datestring == '15.12.2017'

    def test_origin_station(self, recorded_parser):
        assert recorded_parser.origin_station == 'Gießen'

    def test_destination_station(self, recorded_parser):
        assert recorded_parser.destination_station == 'Waldkirch'

    def test_connection_row_parser(self, recorded_parser):
        parser = ConnectionRowParser(recorded_parser.connection_rows[0])
        assert parser.transfers == 2
        assert parser.products == {'IC', 'ICE', 'BSB'}
        assert parser.origin_time == '14:22'
        assert parser.destination_time == '18:28'
