import logging

from app.common.util.decorators import singleton


class OrkgSimCompApiService:

    @singleton
    def __new__(cls, *args, **kwargs):
        pass

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
