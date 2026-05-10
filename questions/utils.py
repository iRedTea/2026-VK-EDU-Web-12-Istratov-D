from PIL import Image


def crop_square(image_path, size=(300, 300)):
    img = Image.open(image_path)

    width, height = img.size

    min_side = min(width, height)

    left = (width - min_side) / 2
    top = (height - min_side) / 2
    right = (width + min_side) / 2
    bottom = (height + min_side) / 2

    img = img.crop((left, top, right, bottom))

    img = img.resize(size)

    img.save(image_path)