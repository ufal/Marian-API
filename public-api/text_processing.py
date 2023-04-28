import re
import unicodedata


class TextProcessor:
    def __init__(self) -> None:
        self.pre_alternatives_first_stage = {
            "，": ",",
            "。 *": ".",
            "、": ",",
            "”": '"',
            "“": '"',
            "∶": ":",
            "：": ":",
            "？": "?",
            "《": '"',
            "》": '"',
            "）": ")",
            "！": "!",
            "（": "(",
            "；": ";",
            "１": '"',
            "」": '"',
            "「": '"',
            "０": "0",
            "３": "3",
            "２": "2",
            "５": "5",
            "６": "6",
            "９": "9",
            "７": "7",
            "８": "8",
            "４": "4",
            "． *": ". ",
            "～": "~",
            "’": "'",
            "…": "...",
            "━": "-",
            "〈": "<",
            "〉": ">",
            "【": "[",
            "】": "]",
            "％": "%",
        }
        self.pre_alternatives_second_stage = {"  *": " ", "^ *": "", " *$": ""}
        self.post_alternatives = {" ": "", "▁": " "}

    def post_process(self, text):
        text = self.replace_chars_with_alternatives(text, self.post_alternatives)
        return text

    def pre_process(self, text):
        text = self.replace_chars_with_alternatives(
            text, self.pre_alternatives_first_stage
        )
        text = self.remove_control_characters_except_new_line(text)
        text = self.replace_chars_with_alternatives(
            text, self.pre_alternatives_second_stage
        )
        return text

    @staticmethod
    def replace_chars_with_alternatives(text, alternatives):
        for key, alternative in alternatives.items():
            regex = r"{}".format(key)
            text = re.sub(regex, alternative, text)
        return text

    @staticmethod
    def remove_control_characters_except_new_line(s):
        return "".join(
            ch for ch in s if ch == "\n" or unicodedata.category(ch)[0] != "C"
        )
