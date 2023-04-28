import os


class EnvParameters:
    def __init__(
        self,
        marian_port=os.environ["MARIAN_PORT"],
        version=os.environ["VERSION"],
        char_limit=os.environ["CHAR_LIMIT"],
        lines_limit=os.environ["LINES_LIMIT"],
    ):
        self.marian_parameters = MarianParameters(marian_port)
        self.api_parameters = APIParameters(version, char_limit, lines_limit)


class MarianParameters:
    def __init__(self, port):
        self.port = port
        self.host = "localhost"


class APIParameters:
    def __init__(self, version, char_limit, lines_limit):
        self.version = version
        self.char_limit = int(char_limit)
        self.lines_limit = int(lines_limit)
