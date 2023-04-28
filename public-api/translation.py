import logging
import re
from text_processing import TextProcessor
from helpers.parameters import EnvParameters


class Translation:
    def __init__(self, marian_ws_connection):
        self.marian_ws_connection = marian_ws_connection
        self.text_processor = TextProcessor()
        self.api_parameters = EnvParameters().api_parameters

        self.server_logger = logging.getLogger("server_logger")
        self.local_logger = logging.getLogger("local_logger")
        self.server_logger.info(
            "Maximum number of lines in a request: {}".format(
                str(self.api_parameters.lines_limit)
            )
        )
        self.server_logger.info(
            "Maximum number of characters in a single line in a request: {}".format(
                str(self.api_parameters.char_limit)
            )
        )

    def batch_translate(self, sentences, tgt):
        sentences_lines = [len(sentence.split("\n")) for sentence in sentences]
        sentences_new_line_separated = "\n".join(sentences)
        translated_sentences = self.translate(sentences_new_line_separated, tgt)
        return self.decouple(translated_sentences, sentences_lines)

    def translate(self, text, tgt):
        self.local_logger.debug("RAW: " + text.replace("\n", "<endl>"))
        text = self.text_processor.pre_process(text)
        text = self.add_tgt_tag(text, tgt)

        self.local_logger.debug("PRE_PROCESSED: " + text.replace("\n", "<endl>"))
        translated_text = self.marian_ws_connection.send_text_to_translate(text)

        self.local_logger.debug("TRANSLATION: " + translated_text.replace("\n", "<endl>"))
        return translated_text

    @staticmethod
    def add_tgt_tag(text, tgt):
        to_tgt = "2{} ".format(tgt)
        text = to_tgt + re.sub(r"[\n](?!$)", "\n" + to_tgt, text)
        return text

    @staticmethod
    def decouple(sentences_coupled, sentences_lines):
        sentences_coupled_separated = sentences_coupled.split("\n")
        decoupled_sentences = []
        start = 0
        for sentence_lines in sentences_lines:
            decoupled_sentences.append(
                "\n".join(sentences_coupled_separated[start: start + sentence_lines])
            )
            start += sentence_lines
        return decoupled_sentences
