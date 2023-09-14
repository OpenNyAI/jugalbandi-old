class BusinessException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        pass


class UnAuthorisedException(BusinessException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 400

    def __str__(self):
        return self.message


class IncorrectInputException(BusinessException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 422

    def __str__(self):
        return self.message


class InternalServerException(BusinessException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 500

    def __str__(self):
        return self.message


class ServiceUnavailableException(BusinessException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 503

    def __str__(self):
        return self.message


class QuotaExceededException(BusinessException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.status_code = 429

    def __str__(self):
        return self.message
