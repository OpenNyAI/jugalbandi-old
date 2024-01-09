import logging


class Logger:
    def __init__(self, engine) -> None:
        self.engine = engine

    async def get_logger(logger_name: str):
        logger = logging.getLogger(logger_name)
        logging.basicConfig(level=logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s"
            " span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
