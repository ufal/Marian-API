from websocket import create_connection
import logging


class MarianWebServerConnection:
    def __init__(self, marian_parameters):
        self.web_socket_connection = None
        self.marian_parameters = marian_parameters
        self.server_logger = logging.getLogger("server_logger")
        self.local_logger = logging.getLogger("local_logger")
        self.server_logger.info(
            "Marian translation engine running on port:{}.".format(
                str(marian_parameters.port)
            )
        )

    def send_text_to_translate(self, text):
        if self.web_socket_connection is None:
            self.create_connection()
        try:
            self.web_socket_connection.send(text)
            received_text = self.web_socket_connection.recv()
            return received_text
        except Exception as e:
            self.server_logger.error("WebSocket connection error - {}".format(str(e).replace("\n", "<endl>")))
            raise e

    def create_connection(self):
        try:
            self.web_socket_connection = create_connection(
                "ws://{}:{}/translate".format(
                    self.marian_parameters.host, self.marian_parameters.port
                )
            )
            self.server_logger.info(
                "WebSocket connection to translation engine successful."
            )
        except Exception as e:
            self.server_logger.error("WebSocket creation error - {}".format(str(e).replace("\n", "<endl>")))
            raise e
