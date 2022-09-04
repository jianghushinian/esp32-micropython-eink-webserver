import json
import socket

from config import BUFFER_SIZE
from networker import networker
from urllib.parse import urlparse


class HTTPClient(object):
    """HTTP 客户端"""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status_code = 200
        self.headers = {}
        self.text = ""

    def __del__(self):
        # 关闭连接
        self.sock.close()

    def connect(self, ip, port):
        """建立连接"""
        self.sock.connect((ip, port))

    def request(self, method, url):
        """请求"""
        # URL 解析
        parse_result = urlparse(url)
        ip = parse_result.hostname
        port = parse_result.port or 80
        host = parse_result.netloc
        path = parse_result.path
        query = parse_result.query
        # 建立连接
        self.connect(ip, port)
        # 构造请求数据
        send_data = f"{method} {path}?{query} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode("utf-8")
        # 发送请求
        self.sock.send(send_data)

        # 处理响应
        data = self.recv_data()
        self.parse_data(data)

    def recv_data(self):
        """接收数据"""
        data = b""
        self.sock.settimeout(1)
        while 1:
            try:
                chunk = self.sock.recv(BUFFER_SIZE)
            except Exception as e:
                print(e)
                break
            data += chunk
            if len(chunk) < BUFFER_SIZE:
                break
        return data.decode("utf-8")

    def parse_data(self, data):
        """解析数据"""
        header, self.text = data.split("\r\n\r\n", 1)
        status_line, header = header.split("\r\n", 1)
        for item in header.split("\r\n"):
            k, v = item.split(": ")
            self.headers[k] = v
        self.status_code = status_line.split(" ")[1]

    def json(self):
        return json.loads(self.text)


def example():
    from config import WEATHER_URL, WIFI_SSID, WIFI_PASSWORD

    networker.connect(WIFI_SSID, WIFI_PASSWORD)
    client = HTTPClient()
    client.request("GET", WEATHER_URL)
    print(f"status_code: {client.status_code}")
    print(f"headers: {client.headers}")
    print(f"text: {client.text}")
    print(f"json: {client.json()}")


if __name__ == "__main__":
    example()
