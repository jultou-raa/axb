import pathlib
import json

def load_json(file_path: pathlib.Path)->dict:
    with pathlib.Path(file_path).open() as fp:
        json_data = json.load(fp)
    return json_data