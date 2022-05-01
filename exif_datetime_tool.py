#!/usr/bin/env python3

from PIL import Image, ExifTags, UnidentifiedImageError
import datetime
import re
import sys
import os
from typing import Optional


EXIF_TAG_STRINGS = {v: k for (k, v) in ExifTags.TAGS.items()}
date_time_source_tags = [
    EXIF_TAG_STRINGS["DateTime"],
    EXIF_TAG_STRINGS["DateTimeOriginal"],
    EXIF_TAG_STRINGS["DateTimeDigitized"],
]
# we set the gathered information on all three of these,
# because different tools use different things ...
date_time_target_tags = [
    EXIF_TAG_STRINGS["DateTime"],
    EXIF_TAG_STRINGS["DateTimeOriginal"],
    EXIF_TAG_STRINGS["DateTimeDigitized"],
]

dir = os.path.realpath(os.path.dirname(__file__))
input_path = os.path.join(dir, "input")
output_path = os.path.join(dir, "output")


date_time_regex_wa = re.compile("IMG-([0-9]{8})-WA")
date_time_regex_plain = re.compile("([0-9]{8})[-_]([0-9]{6})")
date_time_format = "%Y:%m:%d %H:%M:%S"


def try_get_datetime_from_filename(img) -> Optional[str]:
    basename = os.path.basename(img)
    m = date_time_regex_wa.match(basename)
    if m:
        return datetime.datetime.strptime(
            m[1], "%Y%m%d"
        ).strftime(date_time_format)
    m = date_time_regex_plain.match(basename)
    if m:
        return datetime.datetime.strptime(
            f"{m[1]}{m[2]}", "%Y%m%d%H%M%S"
        ).strftime(date_time_format)
    return None


def handle_image(dir_rel, img_name):
    img_path = os.path.join(input_path, dir_rel, img_name)
    try:
        img_pil = Image.open(img_path)
    except (OSError, UnidentifiedImageError) as ex:
        sys.stderr.write(f"{img_path}: failed to open file: {str(ex)}\n")
        return
    try:
        img_exif = img_pil.getexif()
        for dtst in date_time_source_tags:
            dt = img_exif.get(dtst, None)
            if dt is not None:
                break
        if dt is None:
            dt = try_get_datetime_from_filename(img_path)
            if dt is None:
                print(f"{img_path}: failed to parse datetime from filename")
                return
            print(f"{img_path}: interpreting filename date time as {dt}")
        else:
            print(f"{img_path}: keeping existing time value {dt}")
        for dttt in date_time_target_tags:
            if dttt not in img_exif:
                img_exif[dttt] = dt
        img_pil.save(
            os.path.join(output_path, dir_rel, img_name),
            exif=img_exif
        )
    except (OSError, KeyError, ValueError) as ex:
        sys.stderr.write(f" {img_path}: failed to handle image: {str(ex)}\n")
    finally:
        img_pil.close()


def handle_dir(dir_rel):
    os.makedirs(os.path.join(output_path, dir_rel), exist_ok=True)
    for obj in os.scandir(os.path.join(input_path, dir_rel)):
        if obj.is_file():
            if obj.name == ".gitignore":
                continue
            handle_image(dir_rel, obj.name)
            continue
        path = os.path.join(dir_rel, obj.name)
        if obj.is_dir:
            handle_dir(path)
        elif obj.is_symlink:
            sys.stderr.write(f"{path}: ignoring symlink\n")

handle_dir("")
