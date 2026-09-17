Settings → MQTT

MQTT aktivieren
Broker: 192.168.178.114
Port: 1883
keine Verschlüsselung


Noch eine technische Anmerkung

Beim Gen3 ist die Leistungsvariable im Status normalerweise apower. Die Shelly.addStatusHandler()-Methode liefert aber nur Änderungen, nicht zwingend den kompletten Status. Deshalb würde ich nach dem ersten Test einmal prüfen, ob deine Firmware bei Leistungsänderungen tatsächlich delta.apower liefert.

Falls nicht, ist die Anpassung sehr klein: Dann liest der Handler delta anders aus oder wir verwenden den NotifyStatus-Mechanismus.

Der nächste sinnvolle Test wäre:

Script starten.

In der Shelly-Konsole prüfen:

Shelly.addStatusHandler(function(s){print(JSON.stringify(s));});
Ein Gerät mit >250 W ein- und ausschalten.

Dann sieht man exakt, welches Event deine Firmware liefert.
