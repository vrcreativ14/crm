class AutoQuoterException(Exception):
    def __init__(self, msg, extra=None) -> None:
        super().__init__(msg)

        self.extra = extra
