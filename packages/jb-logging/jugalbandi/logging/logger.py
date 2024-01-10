import logging


class Logger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s")

    async def info(self, message: str):
        self.logger.info(message)

    async def debug(self, message: str):
        self.logger.debug(message)

    async def error(self, message: str):
        self.logger.error(message)

    async def exception(self, message: str):
        self.logger.exception(message)

    async def critical(self, message: str):
        self.logger.critical(message)
