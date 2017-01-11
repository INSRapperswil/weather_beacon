# Weather Beacon mit WiPy
Das WiPy Board ist ein Embedded-Plattform für Entwicklungen von IoT Anwendungen. Das Board besitzt Bluetooth LE und WiFi Funkmodule und lässt sich damit einfach mit dem Internet verbinden. Da Board lässt sich einfach mit der Programmiersprache Python programmieren. 
In diesem Tutorial lernen Sie mit wie Sie ein Weather-Beacon Programmieren, welches über die bevorstehenden Regenprognosen informiert. Das Beacon lässt sich so beispielsweise neben dem Regenschirm platzieren und informiert einen beim Verlassen des Hauses, ob man besser einen Schirm mitnehmen soll.
## Vorbereitungen
- pymakr IDE von www.pycom.io herunterladen und installieren.
- Firmware update durchführen mit Firmwareupdate utility

## Erste Schritte
Verbinden Sie das Board via USB Kabel mit ihrem Computer und öffnen Sie ein Terminal auf der entsprechenden seriellen Schnittstelle mit 115200 Baud. Nun gelangen Sie direkt auf den interkativen Python Interpreter des Boards und können mit dem Programmieren loslegen.

## LED
Um die interne LED anzusteuern müssen wir als erstes das pycom Modul laden

    >>> import pycom
    
Standardmässig blinkt die LED in regelmässigen abständen, eine Art Herzschlag (Heartbeat), um dies zu deaktivieren führen Sie folgenden Befehl aus

    >>> pycom.heartbeat(False)
    
Danach lässt sich die Farbe der LED beliebig einstellen. Als Parameter der Funktion rgbled gibt man dazu den RGB Farbcode in hexadezimal ein. RGB steht für Rot Grün Blau. Die Grundfarben. Für jeden dieser Farbkanäle kann man die Helligkeit von 00 bis FF im Format 0xRRGGBB einstellen. Der Wert für komplett Rot ist 0xFF0000, für Grün 0x00FF00, für Blau 0x0000FF und für Gelb, also eine Mischung aus Rot und Grün, 0xFFFF00.

    >>> pycom.rgbled(0xff0000)
    
## LED blinken lassen
Um die LED blinken zu lassen benötigen wir noch das Modul time, welches uns erlaubt eine Pause im Programm einzulegen

    >>> import utime
    >>> while True:
    >>>    pycom.rgbled(0xFF0000)
    >>>    utime.sleep(1)
    >>>    pycom.rgbled(0x000000)
    >>>    utime.sleep(1)
    
Rücken Sie das Programm jeweils mit 4 Leerschlägen ein. Am Schluss sind bis zu 3 Enter eingaben nötig, bevor das Programm zu laufen beginnt. Abbrechen können Sie es, indem Sie CTRL und C gleichzeitig drücken.

## LED Blau Rot blinken
Passen Sie das Programm so an, dass es abwechselnd Rot und Blau blinkt mit einer halben Sekunde Pause dazwischen.


