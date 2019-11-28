import sys
from monkeytype import Config
from monkeytype.tracing import CallTracer
from flask import Flask


class MonkeyType(object):
    def __init__(self, config: Config):
        self.config = config
        self.tracer_logger = config.trace_logger()
        self.tracer = CallTracer(logger=self.tracer_logger,
                                 code_filter=config.code_filter(),
                                 sample_rate=config.sample_rate())

    def init_app(self, app: Flask):
        app.before_request(self.before_request)
        app.teardown_appcontext(self.teardown)

    def before_request(self):
        sys.setprofile(self.tracer)

    def teardown(self, _):
        sys.setprofile(None)
        self.tracer_logger.flush()
