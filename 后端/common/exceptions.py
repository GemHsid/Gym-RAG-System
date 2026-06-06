from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('django')

def custom_exception_handler(exc, context):
    """
    自定义全局异常处理
    统一返回格式: { "code": 500, "message": "Error detail", "data": null }
    """
    # 先调用 DRF 默认处理
    response = exception_handler(exc, context)

    if response is None:
        # 处理 DRF 未捕获的异常 (如 500)
        logger.error(f"Uncaught Exception: {exc}", exc_info=True)
        return Response({
            "code": 500,
            "message": "服务器内部错误，请联系管理员",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 统一 DRF 异常格式
    custom_response_data = {
        "code": response.status_code,
        "message": "请求失败",
        "data": None
    }

    # 提取错误详情
    if isinstance(response.data, dict):
        if 'detail' in response.data:
            custom_response_data['message'] = response.data['detail']
        else:
            # 拼接字段错误 (e.g. {"username": ["该字段必填"]})
            errors = []
            for k, v in response.data.items():
                if isinstance(v, list):
                    errors.append(f"{k}: {'; '.join(v)}")
                else:
                    errors.append(f"{k}: {v}")
            custom_response_data['message'] = " | ".join(errors)
    elif isinstance(response.data, list):
        custom_response_data['message'] = str(response.data[0])

    response.data = custom_response_data
    return response
