from common import clip


def decode(features, threshold):
    threshold = clip(threshold)
    mask = [[int(value >= threshold) for value in row] for row in features]
    points = [(x, y) for y, row in enumerate(mask) for x, value in enumerate(row) if value]
    boxes = []
    if points:
        xs, ys = zip(*points)
        boxes = [{'box': [min(xs), min(ys), max(xs) + 1, max(ys) + 1], 'label': 'object', 'score': 1.0}]
    return {'detections': boxes, 'segmentation': mask}
