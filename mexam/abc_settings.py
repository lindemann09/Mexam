
from __future__ import annotations
from abc import ABCMeta

from os.path import splitext
from typing import Optional
from .misc import FILE_ENCODING

import toml
import yaml

class ABCSettings(metaclass=ABCMeta):

    FILE_ENCODING = FILE_ENCODING

    def __init__(self,
                 filename:Optional[str]=None,
                 parent:Optional[ABCSettings]=None):

        if filename is None and isinstance(parent, ABCSettings):
            self._name = parent._name
            self._ext = parent._ext
            self._settings_dict = parent._settings_dict

        elif isinstance(filename, str) and parent is None:
            # load
            self._name, self._ext = splitext(filename)
            with open(filename, encoding=ABCSettings.FILE_ENCODING) as f:
                if self._ext == ".yaml" or self._ext == ".yml":
                    self._settings_dict = yaml.load(f, Loader=yaml.FullLoader)
                elif self._ext == ".toml":
                    self._settings_dict = toml.load(f)
                else:
                    raise RuntimeError(f"Settings file has to be .yaml or .toml file and not {self._ext}")

        else:
            raise ValueError("Specify either filename or parent!")


    def _mandatory(self, key):
        # get a _mandatory setting (raises error if not defined)
        try:
            return self._settings_dict[key]
        except KeyError as err:
            raise RuntimeError(f"{key} needs to be define in the settings.") from err

    def _optional(self, key, default):
        # get optional setting, returns default if not defined in YAML file
        try:
            return self._settings_dict[key]
        except KeyError:
            return default

    @property
    def name(self):
        return self._name

    @property
    def filename(self):
        return f"{self._name}.{self._ext}"

    def print_file(self):
        print(f"\nSettings file: {self.filename}\n")
        print(str(self))

    def __str__(self):
        if self._ext == ".toml":
            return toml.dumps(self._settings_dict)
        else:
            return yaml.dump(self._settings_dict)
