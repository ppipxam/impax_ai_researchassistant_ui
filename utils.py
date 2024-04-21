from collections import namedtuple
from typing import Union
import os


Numeric = Union[int, float, complex]

DBConfig = namedtuple(
    typename="DBConfig",
    field_names=["db_name", "filter"]
)

USERNAME = os.environ.get("UI_USERNAME")
PASSWORD = os.environ.get("UI_PASSWORD")

# Function to check if the username and password are correct
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD