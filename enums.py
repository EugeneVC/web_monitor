import enum


class CheckStatusEnum(enum.Enum):
    """ Статусы запросов к ресурсу """
    ok = 1
    request_failed = 2
    request_timeout = 3
    content_mismatch = 4
