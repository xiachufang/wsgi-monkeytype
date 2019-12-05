import sys

from monkeytype import Config
from monkeytype.tracing import CallTracer


class MonkeyTypeWsgiMiddleware(object):

    def __init__(self, app, config: Config):
        self.config = config
        self.tracer_logger = config.trace_logger()
        self.tracer = CallTracer(logger=self.tracer_logger,
                                 code_filter=config.code_filter(),
                                 sample_rate=config.sample_rate())
        self.app = app

    def __call__(self, environ, start_response):
        try:
            sys.setprofile(self.tracer)
            return self.app(environ, start_response)
        finally:
            sys.setprofile(None)
            self.tracer_logger.flush()
