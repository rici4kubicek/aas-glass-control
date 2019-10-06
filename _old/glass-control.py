# !/usr/bin/python
from tools import mfrc522, apa102, nanopi_spi
import signal
from timer import timer
import paho.mqtt.client as mqtt

nanopi = nanopi_spi.nanopi_spi()
nanopi.cs_init([6, 7])
nanopi.cs_set(0, 1)
nanopi.open(0,0,100000)

led = apa102.APA102(4)

led.prepare_data(0, 0, 0, 5, 0)
led.prepare_data(0, 0, 0, 5, 1)
led.prepare_data(0, 0, 0, 5, 2)
led.prepare_data(0, 0, 0, 5, 3)
led_blue = led.get_data()
nanopi.cs_set(0, 1)
nanopi.write(led_blue)
nanopi.cs_set(0, 0)

data_send=0
continue_reading = True

timer = timer.Timer()


def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False


signal.signal(signal.SIGINT, end_read)

nanopi.cs_set(1, 1)
MIFAREReader = mfrc522.MFRC522(0, 0, nanopi)

mqttc = mqtt.Client()
mqttc.connect("localhost")
mqttc.publish("test", "ready")

print("Press Ctrl-C to stop.")

# continue_reading = False
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")
        mqttc.publish("test", "card detected")
        timer.start(5)
        data_send = 0
        led.prepare_data(20, 0, 15, 5, 0)
        led.prepare_data(0, 20, 0, 5, 1)
        led.prepare_data(20, 0, 0, 5, 2)
        led.prepare_data(20, 45, 21, 5, 3)
        data = led.get_data()
        nanopi.cs_set(0, 1)
        nanopi.write(data)
        nanopi.cs_set(0, 0)

    # Get the UID of the card
    (status, uid) = MIFAREReader.anticoll(1)

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        print("Card read UID: {}, {}, {}, {}".format(hex(uid[0]), hex(uid[1]), hex(uid[2]), hex(uid[3])))

        MIFAREReader.select_tag(uid)
        # MIFAREReader.MFRC522_SAK(uid)

        MIFAREReader.dump_ultralight(uid)
        MIFAREReader.stop_crypto1()

    if timer.is_expired():
        if data_send != 1:
            led.prepare_data(0, 0, 0, 5, 0)
            led.prepare_data(0, 0, 0, 5, 1)
            led.prepare_data(0, 0, 0, 5, 2)
            led.prepare_data(0, 0, 0, 5, 3)
            data = led.get_data()
            nanopi.cs_set(0, 1)
            nanopi.write(data)
            nanopi.cs_set(0, 0)
            data_send = 1