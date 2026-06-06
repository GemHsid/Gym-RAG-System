from rest_framework.response import Response


def ok(data=None, message="OK", code=0, http_status=200):
    return Response({"code": code, "message": message, "data": data}, status=http_status)


def fail(message="请求失败", code=400, http_status=400, data=None):
    return Response({"code": code, "message": message, "data": data}, status=http_status)

