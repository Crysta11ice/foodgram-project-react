from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler


def error_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 400:
            for error in response.data:
                if response.data[error] == [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]:
                    response.data[error] = 'Поле обязательно для заполнения'

        if response.status_code == 401:
            response.data['detail'] = 'Ошибка предоставления данных'

        if response.status_code == 403:
            response.data[
                'detail'
            ] = 'Недостаточно прав для выполнения действия'

        if response.status_code == 404:
            response.data['detail'] = 'Страница не найдена'

    return response
