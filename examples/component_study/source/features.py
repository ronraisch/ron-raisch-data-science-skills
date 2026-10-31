from common import clip


def extract(pixels):
    return [[clip(value / 255.0) for value in row] for row in pixels]
