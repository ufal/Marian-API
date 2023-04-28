from cerberus import Validator


class CustomValidator(Validator):
    def __init__(self, lines_limit, char_limit, *args, **kwargs):
        super(CustomValidator, self).__init__(*args, **kwargs)
        self.lines_limit = lines_limit
        self.char_limit = char_limit

    def _check_with_list_of_strings(self, field, value):
        if isinstance(value, list) and not all(isinstance(item, str) for item in value):
            message = f"Input list elements should only contain string values."
            self._error(field, message)

    def _check_with_limit_lines_number(self, field, value):
        try:
            if not self.check_lines(value):
                message = f"Too long text in the request. Maximum total number of lines in the whole text:" \
                            f"{str(self.lines_limit)}."
                self._error(field, message)
        except Exception as e:
            pass

    def _check_with_limit_char_number(self, field, value):
        try:
            if not self.check_chars(value):
                message = f"Too long sentence in the request: {value}. Make sure that paragraphs are properly " \
                          f"separated by newline. Maximum number of characters in a single " \
                          f"sentence: {str(self.char_limit)}."
                self._error(field, message)
        except Exception as e:
            pass

    def check_lines(self, value):
        value_to_check = None
        if isinstance(value, list):
            value_to_check = "\n".join(value)
        else:
            value_to_check = value
        if len(value_to_check.split("\n")) > self.lines_limit:
            return False
        return True

    def check_chars(self, value):
        value_to_check = None
        if isinstance(value, list):
            value_to_check = "\n".join(value)
        else:
            value_to_check = value
        for line in value_to_check.split("\n"):
            if len(line) > self.char_limit:
                return False
        return True
