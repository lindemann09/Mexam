from typing import Optional
from ..abc_settings import ABCSettings

class MarkdownSettings(ABCSettings):

    EXAMPLE = """# Markdown database settings
md_database: data
"""

    @property
    def md_database(self) -> Optional[str]:
        return self._optional("md_database", default=None)

    @property
    def db_file(self) -> Optional[str]:
        return self._optional("db_file", default=None)
