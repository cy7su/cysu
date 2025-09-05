"""
Утилиты для работы с поддоменами
"""
from flask import request, url_for
from urllib.parse import urlparse

def get_subdomain_url_for(endpoint, **values):
    """
    Генерирует URL с правильным доменом (поддомен или основной)
    в зависимости от текущего запроса
    """
    # Получаем базовый URL через url_for
    base_url = url_for(endpoint, **values)
    
    # Если это поддомен (не основной домен)
    if (hasattr(request, 'host') and request.host and '.' in request.host and 
        not request.host.startswith('www.') and request.host != 'cysu.ru'):
        
        # Проверяем, является ли URL уже абсолютным
        if base_url.startswith('http://') or base_url.startswith('https://'):
            # Если URL уже абсолютный, заменяем домен
            parsed = urlparse(base_url)
            return f"https://{request.host}{parsed.path}{'?' + parsed.query if parsed.query else ''}{'#' + parsed.fragment if parsed.fragment else ''}"
        else:
            # Если URL относительный, добавляем протокол и домен
            return f"https://{request.host}{base_url}"
    
    # Для основного домена возвращаем как есть
    return base_url

def get_subdomain_redirect(endpoint, **values):
    """
    Создает редирект с правильным доменом
    """
    from flask import redirect
    url = get_subdomain_url_for(endpoint, **values)
    return redirect(url)

def is_subdomain():
    """
    Проверяет, является ли текущий запрос поддоменом
    """
    return (hasattr(request, 'host') and request.host and '.' in request.host and 
            not request.host.startswith('www.') and request.host != 'cysu.ru')

def get_current_domain():
    """
    Возвращает текущий домен (с поддоменом или без)
    """
    if hasattr(request, 'host') and request.host:
        return request.host
    return 'cysu.ru'
