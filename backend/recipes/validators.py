import re
from django.core.exceptions import ValidationError

from foodgram_project.settings import BAD_NAMES, REGEX

NOT_REGEX_NAME = 'Нельзя использовать в имени: {}'
FORBIDDEN_NAME = '{} использовать нельзя в качестве имени пользователя!'


def validate_username(name):
    if name in BAD_NAMES:
        raise ValidationError(FORBIDDEN_NAME.format(name))
    used_wrong_chars = ''.join(set(re.sub(REGEX, '', name)))
    if used_wrong_chars:
        raise ValidationError(
            NOT_REGEX_NAME.format(used_wrong_chars)
        )
    return name