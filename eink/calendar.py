from machine import Pin, SPI, RTC
import ntptime
import time

from eink.libs import adafruit_framebuf as framebuf
from eink.libs import epaper4in2 as epaper

from config import NTP_HOST, NTP_DELTA, WIFI_SSID, WIFI_PASSWORD
from eink.imgs import calendar
from networker import networker


def get_week_by_date(y, m, d):
    """根据年月日计算星期几"""
    y = y - 1 if m in [1, 2] else y
    m = 13 if m == 1 else (14 if m == 2 else m)
    w = (d + 2 * m + 3 * (m + 1) // 5 + y + y // 4 - y // 100 + y // 400) % 7 + 1
    return w


def is_leap_year(y):
    """是否为闰年"""
    return y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)


def get_days_in_month(y, m):
    """根据年月计算当月天数"""
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    else:
        return 29 if is_leap_year(y) else 28


def sync_ntp():
    """同步网络时间"""
    networker.connect(WIFI_SSID, WIFI_PASSWORD)

    ntptime.host = NTP_HOST
    ntptime.NTP_DELTA = NTP_DELTA
    try:
        ntptime.settime()
        # print("synchronize ntp succeed")
    except Exception as e:
        print(e)


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
    buf = calendar.image_array
    fb = framebuf.FrameBuffer(buf, h, w, framebuf.MHMSB)
    return fb, buf


def show(fb, buf, epd):
    black = 0
    white = 1

    fb.rotation = 3

    # 记录上次矩形的左上角坐标
    last_rect_x = 0
    last_rect_y = 0
    # 记录上次显示的所有数字左上角坐标
    last_number_x_y = []

    def show_text(year, month, day):
        nonlocal last_rect_x, last_rect_y, last_number_x_y
        # 清空上次显示的数字
        for content, x, y in last_number_x_y:
            fb.text(content, x, y, white)

        # 清空列表
        last_number_x_y = []

        # 显示 title
        fb.text(" Mon Tue Wed Thu Fri Sat Sun", 0, 15, black)
        print(" Mon Tue Wed Thu Fri Sat Sun")
        fb.hline(0, 30, 180, black)
        print("-" * 30)

        content = ""
        row = 3
        today_row = 0
        today_col = 0
        # 计算这个月有多少天
        days = get_days_in_month(year, month)

        for d in range(1, days + 1):
            # 计算星期几
            w = get_week_by_date(year, month, d)

            if d == 1:
                content = content + "    " * (w - 1)
            else:
                if w == 1:
                    fb.text(content, 0, row * 15 - 5, black)
                    print(content)
                    last_number_x_y.append([content, 0, row * 15 - 5])
                    row += 1
                    content = ""
            content = content + f"  {d:2d}"

            if d == day:
                today_row = row
                today_col = w

        if content:
            fb.text(content, 0, row * 15 - 5, black)
            print(content)
            last_number_x_y.append([content, 0, row * 15 - 5])

        rect_x = (today_col - 1) * 24 + 5
        rect_y = today_row * 15 - 8

        # 清空上次显示的矩形
        if last_rect_x != 0 and last_rect_y != 0:
            fb.rect(last_rect_x, last_rect_y, 22, 14, white)
            print(f"last_rect_x: {last_rect_x}, last_rect_y: {last_rect_y}")

        last_rect_x, last_rect_y = rect_x, rect_y

        fb.rect(rect_x, rect_y, 22, 14, black)

        epd.display_frame(buf)

    rtc = RTC()
    date = rtc.datetime()
    show_text(date[0], date[1], date[2])  # 年月日


def run():
    sync_ntp()
    spi = create_spi()
    epd = create_epd(spi)
    fb, buf = create_frame_buffer()
    show(fb, buf, epd)


if __name__ == "__main__":
    run()
