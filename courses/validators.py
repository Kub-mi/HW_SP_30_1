from urllib.parse import urlparse
from django.core.exceptions import ValidationError
import re

# Разрешаем только youtube.com (и его поддомены www., m.)
_ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com"}

def _is_allowed_youtube(url: str) -> bool:
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.netloc in _ALLOWED_HOSTS

def validate_youtube_url(value: str):
    if not _is_allowed_youtube(value):
        raise ValidationError("Разрешены только ссылки на youtube.com (http/https).")

class OnlyYouTubeValidator:
    def __init__(self, field: str):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)
        try:
            validate_youtube_url(value)
        except ValidationError as e:
            raise ValidationError({self.field: e.messages})


# --- ДОПОЛНИТЕЛЬНО: если "материалы" — это текст с несколькими ссылками ---
_URL_RE = re.compile(r"https?://[^\s)]+", flags=re.IGNORECASE)

def validate_text_has_only_youtube_links(value: str):
    """
    Находит все URL в тексте и отклоняет любые, которые не на youtube.com.
    Если в тексте нет ссылок — ок.
    """
    if not value:
        return
    bad = []
    for url in _URL_RE.findall(value):
        if not _is_allowed_youtube(url):
            bad.append(url)
    if bad:
        raise ValidationError(
            f"Найдены запрещённые ссылки: {', '.join(bad)}. "
            "Разрешены только ссылки на youtube.com."
        )