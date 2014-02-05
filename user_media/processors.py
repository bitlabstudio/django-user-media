"""Image processors for easy_thumbnails."""


def crop_box(im, box=False, **kwargs):
    """Uses box coordinates to crop an image without resizing it first."""
    if box:
        im = im.crop(box)
    return im
