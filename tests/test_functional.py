import pendulum
import pytest
from schiene2 import ConnectionList, Station


@pytest.mark.functional
def test_functional(betamax_session, monkeypatch):
    monkeypatch.setattr('schiene2.mobile_page.requests', betamax_session)

    # Stephan möchte mit der nächsten Verbindung von Berlin nach
    # nach Bergisch Gladbach fahren und sucht daher die nächsten Verbindungen
    connections = ConnectionList.search(
        'Berlin Ostbahnhof',
        'Bergisch Gladbach',
        pendulum.create(2017, 12, 17, 14, 30, tz='Europe/Berlin')
    )

    # Er bekommt 5 Verbindungen angezeigt
    assert len(connections) == 5

    # Ohne weitere Abfrage, können die Zeiten und die Zahl der
    # Umstiege dargestellt werden
    connection = connections[1]
    assert connection.__str__() == '\n14:31: Berlin Ostbahnhof\n' \
                                   '  Umstiege: 2\n' \
                                   '  Dauer: 5:06\n' \
                                   '  Produkte: ICE, S\n' \
                                   '19:37: Bergisch Gladbach'

    # Um Umsteigebahnhöfe und weitere Details zu erhalten, können diese explizit
    # abgefragt werden
    connection = connection.get_details()

    # Die Umsteigebahnhöfe sind eine Liste von Objekten des Typs Station
    transition_stations = connection.transition_stations
    berlin = Station('Berlin Hbf (tief)')
    cologne = Station('Köln Hbf')
    assert transition_stations == [berlin, cologne]

    # In Berlin verpasst Hans seinen Anschlusszug und sucht nach einer neuen Verbindung
    new_part_connections = connection.search_after_missed_at_station(berlin)

    # Er entscheidet sich den nächstmöglichen Anschlusszug zu nehmen
    connection.update_after_station(cologne, new_part_connections[0])

    # Schon jetzt ist absehbar, dass der Zug in Köln 2 Minuten verspätet ankommen wird
    connection.journeys[1].arrival.delay.in_minutes() == 2

    # Trotzdem bekommt er seinen Anschlusszug in Köln. In Bergisch Gladbach wird er dann
    # um 22:37 ankommen
    assert connection.destination.time.strftime('%H:%M') == '22:37'

    # Dabei hat er eine Verspätung von 180 Minuten
    assert connection.delay_at_destination.in_minutes() == 180
