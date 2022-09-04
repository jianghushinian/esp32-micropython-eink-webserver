import os

# 服务监听地址
HOST = "0.0.0.0"
PORT = 8000

# 缓冲大小
BUFFER_SIZE = 1024

# 首页
HOME_PAGE = "index.html"

# WI-FI
WIFI_SSID = "ssid"
WIFI_PASSWORD = "password"
WIFI_CONNECT_TIMEOUT = 5

# NTP
NTP_HOST = "ntp1.aliyun.com"
NTP_DELTA = 3155644800  # 东八区 UTC+8 偏移时间（秒）

# 天气接口（https://lbs.amap.com/api/webservice/guide/api/weatherinfo）
WEATHER_URL = f"http://restapi.amap.com/v3/weather/weatherInfo?city={cidy_code}&key={key}"
