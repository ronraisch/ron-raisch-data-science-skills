import json
from pathlib import Path
from features import extract
from decoder import decode


def predict(inputs, artifacts):
    checkpoint = json.loads(Path(artifacts['checkpoint']).read_text())
    return decode(extract(inputs['pixels']), checkpoint['threshold'])
