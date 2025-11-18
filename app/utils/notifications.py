from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from flask import redirect, url_for


def redirect_with_notification(
    endpoint_or_url, message, notification_type="info", **url_params
):
    """
    Редирект с уведомлением через URL параметры
    Args:
        endpoint_or_url: Flask endpoint или полный URL
        message: Текст уведомления
        notification_type: Тип уведомления (success, error, warning, info)
        **url_params: Дополнительные параметры для url_for
    """
    if (
        endpoint_or_url.startswith("http://")
        or endpoint_or_url.startswith("https://")
        or endpoint_or_url.startswith("/")
    ):
        url = endpoint_or_url
    else:
        url = url_for(endpoint_or_url, **url_params)
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params["notify"] = [message]
    query_params["notify_type"] = [notification_type]
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )
    return redirect(new_url)
