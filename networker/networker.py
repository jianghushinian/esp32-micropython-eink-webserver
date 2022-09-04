import network
import time

from config import WIFI_CONNECT_TIMEOUT


def connect(ssid, password):
    """连接指定 WI-FI 网络"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    networks = wlan.scan()
    for n in networks:
        if n[0] == ssid.encode("utf-8"):
            break
    else:
        print(f"networks: {networks}")
        raise Exception(f"WI-FI ssid {ssid} not found")

    if not wlan.isconnected():
        wlan.connect(ssid, password)
        start = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) >= WIFI_CONNECT_TIMEOUT * 1000:
                raise Exception(f"WI-FI connect timeout")

    return wlan.config("mac"), wlan.ifconfig()


def example():
    from config import WIFI_SSID, WIFI_PASSWORD

    connect(WIFI_SSID, WIFI_PASSWORD)
    print("mac:", wlan.config("mac"))
    print("ifconfig:", wlan.ifconfig())


if __name__ == "__main__":
    example()
