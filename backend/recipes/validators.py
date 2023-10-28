import re

from django.core.exceptions import ValidationError

from foodgram_project.settings import REGEX_NAME

NOT_REGEX_NAME = 'Нельзя использовать в имени: {}'


def validate_username(name):
    if (used_wrong_chars := ''.join(set(re.sub(REGEX_NAME, '', name)))):
        raise ValidationError(
            NOT_REGEX_NAME.format(used_wrong_chars))
    return name
