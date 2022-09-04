import json

from urllib.parse import unquote_plus


class Request(object):
    """请求类"""

    def __init__(self, request_message):
        method, path, headers, args, form = self.parse_data(request_message)
        self.method = method
        self.path = path
        self.headers = headers
        self.args = args  # query
        self.form = form  # body

    def parse_data(self, data):
        header, body = data.split("\r\n\r\n", 1)
        method, path, headers, args = self._parse_header(header)
        form = self._path_body(body)

        return method, path, headers, args, form

    def _parse_header(self, data):
        request_line, request_header = data.split("\r\n", 1)

        # 请求行拆包 "GET /index HTTP/1.1" -> ["GET", "/index", "HTTP/1.1"]
        method, path_query, _ = request_line.split()
        path, args = self._parse_path(path_query)

        headers = {}
        for header in request_header.split("\r\n"):
            k, v = header.split(": ", 1)
            headers[k] = v

        return method, path, headers, args

    @staticmethod
    def _parse_path(data):
        args = {}
        # 请求路径和 GET 请求参数格式: /index?edit=1&content=text
        if "?" not in data:
            path, query = data, ""
        else:
            path, query = data.split("?", 1)
            for q in query.split("&"):
                k, v = q.split("=", 1)
                args[k] = v
        return path, args

    @staticmethod
    def _path_body(data):
        form = {}
        if data:
            # POST 请求体参数格式: username=zhangsan&password=mima
            for b in data.split("&"):
                k, v = b.split("=", 1)
                form[k] = unquote_plus(v)
        return form


class Response(object):
    """响应类"""
    reason_phrase = {
        200: "OK",
        405: "METHOD NOT ALLOWED",
    }

    def __init__(self, body, headers=None, status=200):
        _headers = {
            "Content-Type": "text/html; charset=utf-8",
        }

        if headers is not None:
            _headers.update(headers)
        self.headers = _headers
        self.body = body
        self.status = status

    def __str__(self):
        # 状态行 "HTTP/1.1 200 OK\r\n"
        header = f"HTTP/1.1 {self.status} {self.reason_phrase.get(self.status, '')}\r\n"
        header += "".join(f"{k}: {v}\r\n" for k, v in self.headers.items())

        blank_line = "\r\n"
        body = self.body

        # body 支持 str 或 bytes 类型
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        response_message = (header + blank_line) + body
        return response_message


class JsonResponse(Response):
    """json 响应类"""

    def __init__(self, data=None, status=200):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }
        if data is None:
            data = {}
        body = json.dumps(data)
        super().__init__(body, headers, status)
