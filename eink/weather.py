from machine import Pin, SPI
import time

from eink.libs import adafruit_framebuf as framebuf
from eink.libs import epaper4in2 as epaper

from config import WIFI_SSID, WIFI_PASSWORD, WEATHER_URL
from eink.imgs.weather import sunshine
from http import client
from networker import networker


def create_spi():
    sck = Pin(18)
    miso = Pin(19)
    mosi = Pin(23)
    spi = SPI(2, baudrate=10000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)
    return spi


def create_epd(spi):
    cs = Pin(33)
    dc = Pin(32)
    rst = Pin(19)
    busy = Pin(35)
    epd = epaper.EPD(spi, cs, dc, rst, busy)
    epd.init()
    return epd


def create_frame_buffer():
    w = 296
    h = 128
    buf = sunshine.image_array
    fb = framebuf.FrameBuffer(buf, h, w, framebuf.MHMSB)
    return fb, buf


def fetch_weather():
    networker.connect(WIFI_SSID, WIFI_PASSWORD)

    cli = client.HTTPClient()
    cli.request("GET", WEATHER_URL)
    data = cli.json()
    return data.get("lives", [{}])[0]


def show(fb, buf, epd):
    black = 0
    white = 1

    weather = fetch_weather()
    windpower = weather["windpower"][-1]
    humidity = weather["humidity"]
    temperature = weather["temperature"]
    # print(windpower, humidity, humidity)

    fb.rotation = 3
    fb.text(windpower, 105, 30, black, size=2)
    fb.text(f"{humidity}%", 105, 85, black, size=2)
    fb.text(temperature, 215, 42, black, size=2)

    epd.display_frame(buf)


def run():
    spi = create_spi()
    epd = create_epd(spi)
    fb, buf = create_frame_buffer()
    show(fb, buf, epd)


if __name__ == "__main__":
    run()
