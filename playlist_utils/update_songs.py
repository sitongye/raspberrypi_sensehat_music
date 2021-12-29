import json
import os

with open(os.path.join("..", "config.json")) as file:
    CONFIG = json.load(file)

#TO DO: check if are new songs that are not included in pathuri
