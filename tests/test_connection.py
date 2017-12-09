import pytest
import pendulum

from schiene2.models import Connection

@pytest.mark.xfail
def test_can_create_by_search():
    #todo mock actual search method when implemented
    connection = Connection.search(
        'Frankfurt Hbf',
        'Freiburg Hbf',
        pendulum.create(2017, 12, 9, 14, 57)
    )
    assert isinstance(connection, Connection)
