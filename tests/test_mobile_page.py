import pendulum
import pytest

from unittest.mock import MagicMock

from schiene2.mobile_page import ConnectionListParser
from schiene2 import mobile_page


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
