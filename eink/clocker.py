from machine import Pin, SPI
import _thread as threading
import time

from eink.libs import adafruit_framebuf as framebuf
from eink.libs import epaper4in2 as epaper


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
    buf = bytearray(w * h // 8)
    fb = framebuf.FrameBuffer(buf, h, w, framebuf.MHMSB)
    return fb, buf


def show(fb, buf, epd, thread_set, lock):
    fb.rotation = 3

    def show_text(t):
        black = 0
        white = 1
        fb.fill(white)

        # 时间
        fb.text(f"{t[3]:02d}:{t[4]:02d}", 100, 30, black, size=4)

        # 水平分割线
        fb.hline(20, 70, 256, black)

        # 星期
        # fb.text("Wed", 170, 100, black, size=2)

        # 日期
        fb.text(f"{t[1]}/{t[2]}", 220, 100, black, size=2)

        epd.display_frame(buf)

    pre_time = now_time = time.localtime()
    show_text(now_time)

    # 记录当前线程
    lock.acquire()
    tid = threading.get_ident()
    thread_set[tid] = False
    lock.release()

    while 1:
        # 接收信号并销毁当前线程
        tid = threading.get_ident()
        if thread_set[tid]:
            lock.acquire()
            del thread_set[tid]
            lock.release()
            break

        if now_time[4] != pre_time[4]:
            show_text(now_time)

        time.sleep(1)
        pre_time = now_time
        now_time = time.localtime()


def run(thread_set, lock):
    spi = create_spi()
    epd = create_epd(spi)
    fb, buf = create_frame_buffer()
    show(fb, buf, epd, thread_set, lock)


if __name__ == "__main__":
    thread_set = {}
    lock = threading.allocate_lock()
    run(thread_set, lock)
