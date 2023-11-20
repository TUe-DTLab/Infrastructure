import os
import pathlib

from dotenv import dotenv_values

path = pathlib.Path(__file__).parent.resolve()

config = {**dotenv_values(path / "../.env"), **os.environ}
