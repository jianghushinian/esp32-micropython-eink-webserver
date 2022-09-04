import _thread as threading
import socket

from config import HOST, PORT, BUFFER_SIZE, HOME_PAGE, WIFI_SSID, WIFI_PASSWORD
from eink.calendar import run as calendar
from eink.clocker import run as clocker
from eink.screensaver import run as screensaver
from eink.weather import run as weather
from http.http import Request, Response, JsonResponse
from networker import networker

thread_set = {}
lock = threading.allocate_lock()


def index(request):
    del request
    with open(HOME_PAGE) as f:
        body = "".join(f.readlines())
        return Response(body)


def switch_pattern(request):
    pattern = request.form.get("pattern", "screensaver")

    if pattern == "screensaver":
        screensaver()
    elif pattern == "weather":
        weather()
    elif pattern == "calendar":
        calendar()
    elif pattern == "clocker":
        threading.start_new_thread(clocker, (thread_set, lock))

    return JsonResponse()


routes = {
    "/": (index, ["GET"]),
    "/switch": (switch_pattern, ["POST"]),
}


def make_response(request, headers=None):
    status = 200
    try:
        route, methods = routes.get(request.path)
    except TypeError:
        return str(JsonResponse({"msg": "request path not found"}, status=404)).encode("utf-8")

    if request.method not in methods:
        return str(JsonResponse({"msg": "request method not allowed"}, status=405)).encode("utf-8")

    data = route(request)

    # 如果返回结果为 Response 对象，直接获取响应报文
    if isinstance(data, Response):
        response_bytes = str(data).encode("utf-8")
    else:
        # 返回结果为字符串，需要先构造 Response 对象，然后再获取响应报文
        response = Response(data, headers=headers, status=status)
        response_bytes = str(response).encode("utf-8")

    # print(f"response_bytes: {response_bytes}")
    return response_bytes


def process_connection(sock):
    # 发送信号终止全部子线程
    for th in thread_set:
        lock.acquire()
        thread_set[th] = True
        lock.release()
    # print("thread_set:", thread_set)

    data = b""
    sock.settimeout(1)
    while 1:
        try:
            chunk = sock.recv(BUFFER_SIZE)
        except Exception as e:
            print(e)
            break
        data += chunk
        if len(chunk) < BUFFER_SIZE:
            break

    # 请求报文
    request_message = data.decode("utf-8")
    # print(f"request_message: {request_message}")

    if not request_message:
        print("request_message is empty")
        sock.close()
        return

    # 解析请求报文
    request = Request(request_message)
    del request_message

    # 根据请求报文构造响应报文
    try:
        response_bytes = make_response(request)
        del request
    except Exception as e:
        print(e)
        response_bytes = str(JsonResponse({"msg": str(e)}, status=500)).encode("utf-8")

    sock.sendall(response_bytes)
    sock.close()


def run():
    # 连接 WI-FI
    _, ifconfig = networker.connect(WIFI_SSID, WIFI_PASSWORD)
    print(f"host ip: {ifconfig[0]}")

    # 显示屏保
    screensaver()

    # 启动 Web Server
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"running on http://{HOST}:{PORT}")

    while 1:
        try:
            sock, address = s.accept()
            print(f"client address: {address}")
            # 启动新的子线程处理
            threading.start_new_thread(process_connection, (sock,))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    run()
