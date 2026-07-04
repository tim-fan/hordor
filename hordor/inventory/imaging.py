import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_DIMENSION = 2500
JPEG_QUALITY = 90


def compress_image_file(file_obj):
    """
    Re-encode an image as a JPEG capped at MAX_DIMENSION on its long edge,
    at JPEG_QUALITY. Returns a ContentFile of the result.
    """
    file_obj.seek(0)
    img = Image.open(file_obj)
    img.load()
    img = ImageOps.exif_transpose(img)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
    return ContentFile(buffer.getvalue())


def as_jpg_name(name):
    """
    Keep existing .jpg/.jpeg names as-is; rename anything else (e.g. .png)
    to .jpg, since compress_image_file always re-encodes as JPEG.
    """
    base, ext = os.path.splitext(name)
    if ext.lower() in ('.jpg', '.jpeg'):
        return name
    return base + '.jpg'


def rotate_image_field(field_file, degrees=-90):
    """
    Rotate an already-saved ImageField file in place (default: 90
    degrees clockwise) and re-save it as JPEG. Writes under a fresh
    filename (old file is only deleted after the new one is written)
    so the URL changes and browsers won't serve a stale cached copy
    of the old orientation, then deletes the old file.

    Does not save the owning model instance -- call instance.save()
    with the relevant field afterwards.
    """
    old_name = field_file.name
    field_file.open('rb')
    img = Image.open(field_file)
    img.load()
    field_file.close()

    rotated = img.rotate(degrees, expand=True)
    buffer = BytesIO()
    rotated.save(buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)

    field_file.save(os.path.basename(as_jpg_name(old_name)), ContentFile(buffer.getvalue()), save=False)
    field_file.storage.delete(old_name)
