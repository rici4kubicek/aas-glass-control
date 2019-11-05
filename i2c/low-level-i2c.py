#!/usr/bin/python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import os
import fnmatch
import time
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

__author__ = "Richard Kubicek"
__copyright__ = "Copyright 2019, FEEC BUT Brno"
__credits__ = ["Richard Kubicek"]
__license__ = "Proprietary"
__version__ = "1.0.0"
__maintainer__ = "Richard Kubicek"
__email__ = "xkubic35@vutbr.cz"
__status__ = "Private Beta"

LL_I2C_TOPIC = "i2c"
LL_DISPLAY_TOPIC = LL_I2C_TOPIC + "/display"
LL_I2C_MSG_TOPIC = LL_I2C_TOPIC + "/msg"


class AasI2C(object):
    def __init__(self):
        self.display = None
        self.fonts = {}
        self.write_text = {}
        self.write_text_flag = False

    def load_fonts(self, size):
        path = './static/'

        files = os.listdir(path)
        pattern = "*.ttf"
        for font in files:
            if fnmatch.fnmatch(font, pattern):
                self.fonts[font[:-4] + "-" + str(size) + ""] = ImageFont.truetype("" + path + font + "", size)


def on_connect(mqtt_client, obj, flags, rc):
    global mqtt_ready
    if rc==0:
        mqtt_ready = 1
        mqttc.subscribe(LL_DISPLAY_TOPIC)
    else:
        mqtt_ready = 0
        retry_time = 2
        while rc != 0:
            time.sleep(retry_time)
            try:
                rc = mqtt_client.reconnect()
            except Exception as e:
                rc = 1
                retry_time = 10  # probably wifi/internet problem so slow down the reconnect periode


if __name__ == "__main__":

    mqttc = mqtt.Client()
    mqttc.connect("localhost")
    mqttc.publish(LL_I2C_MSG_TOPIC, "I2C is prepared")
    mqttc.on_connect = on_connect
    # mqttc.user_data_set(aas)
    # mqttc.message_callback_add(LL_DISPLAY_TOPIC, on_display)

    disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus='0')
    disp.begin()
    disp.clear()
    disp.display()
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # create object
    draw = ImageDraw.Draw(image)
    # clear display
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # load basic font

    font = ImageFont.truetype('static/Vafle_VUT_Regular.ttf', 15)

    draw.text((0,0), u"žluťoučký kůň", font=font, fill=255)

    disp.image(image)
    disp.display()

