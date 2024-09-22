from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from account.logging_config import logger

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework.exceptions import APIException


class CustomValidationError(APIException):
    status_code = 400
    default_detail = 'Validation failed.'
    default_code = 'invalid'


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Handle specific exceptions and customize the response
    if isinstance(exc, ValidationError) and response is not None:
        # Extract error messages and include field names
        error_messages = []
        for field, errors in response.data.items():
            for error in errors:
                error_messages.append(f"{field} {str(error)}")
        combined_error_message = ', '.join(error_messages)

        custom_response_data = {
            "success": False,
            "message": combined_error_message
        }
        return Response(custom_response_data, status=response.status_code)
    elif isinstance(exc, CustomValidationError):
        # پردازش پیام خطا به فرمت دلخواه
        error_messages = []
        for field, error in exc.detail.items():
            error_messages.append(f"{field} {error}")

        combined_error_message = ', '.join(error_messages)

        custom_response_data = {
            "success": False,
            "message": combined_error_message
        }
        return Response(custom_response_data, status=exc.status_code)
    elif isinstance(exc, NotAuthenticated):
        custom_response_data = {
            'success': False,
            'message': 'اطلاعات احراز هویت یافت نشد'
        }
        return Response(custom_response_data, status=response.status_code)

    elif isinstance(exc, AuthenticationFailed):
        custom_response_data = {
            'success': False,
            'message': 'هیچ اکانت فعالی با مشخصاتی که وارد کردید یافت نشد'
        }
        return Response(custom_response_data, status=response.status_code)

    elif isinstance(exc, PermissionDenied):
        custom_response_data = {
            'success': False,
            'message': 'شما مجوز های لازم برای انجام این کار را ندارید'
        }
        return Response(custom_response_data, status=response.status_code)

    # Add custom handling for other exceptions as needed
    elif response is not None:
        custom_response_data = {
            'success': False,
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        }
        return Response(custom_response_data, status=response.status_code)

    return response
