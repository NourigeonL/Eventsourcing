class GenericError(Exception):
    def __init__(self, message : str = "") -> None:
        self.message = message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.message})"

    def json(self) -> dict:
        return {"ErrorType" : self.__class__.__name__, "message":self.message}

class AggregateNotFoundError(GenericError): ...
class InvalidOperationError(GenericError): ...
class ArgumentError(GenericError): ...
class ConcurrencyError(GenericError): ...