from ..misc import strip_lines

class Answer(object):

    ENUM_TAG_CORRECT = "- *X* "
    ENUM_TAG_INCOR   = "- "

    def __init__(self, text: str,
                 is_correct: bool,
                 fixed_position: bool = True):
        self.text = strip_lines(text)
        self.is_correct = is_correct
        self.fixed_position = fixed_position

    def to_text(self) -> str:
        if self.is_correct:
            rtn = self.ENUM_TAG_CORRECT
        else:
            rtn = self.ENUM_TAG_INCOR
        return rtn + self.text + "\n"

    def __str__(self):
        return self.to_text()
