import re

from django.core.exceptions import ValidationError

from foodgram_project.settings import REGEX_USERNAME

NOT_REGEX_NAME = 'Нельзя использовать в имени: {}'


def validate_username(name):
    if (used_wrong_chars := ''.join(set(re.sub(REGEX_USERNAME, '', name)))):
        raise ValidationError(
            NOT_REGEX_NAME.format(used_wrong_chars))
    return name
