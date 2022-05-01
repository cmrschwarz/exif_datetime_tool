#!/usr/bin/env python3

from pyexiv2 import Image
import pyexiv2

import datetime
import re
import sys
import os
from typing import Optional


# this stops pyexiv2 from failing with error messages like:
# 'Directory Canon with 7424 entries considered invalid not read.'
# it is described here: https://github.com/LeoHsiao1/pyexiv2/issues/58
pyexiv2.set_log_level(4)

date_time_source_tags = [
    "Exif.Image.DateTime",
    "Exif.Photo.DateTimeOriginal",
    "Exif.Photo.DateTimeDigitized"
]
# we set the gathered information on all three of these,
# because different tools use different things ...
date_time_target_tags = date_time_source_tags


dir = os.path.realpath(os.path.dirname(__file__))

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
    img_path = os.path.join(dir_rel, img_name)
    try:
        img_ex = Image(img_path)
    except (OSError, RuntimeError) as ex:
        sys.stderr.write(f"{img_path}: failed to parse file: {str(ex)}\n")
        return
    try:
        exif = img_ex.read_exif()
        for dtst in date_time_source_tags:
            dt = exif.get(dtst, None)
            if dt is not None:
                break
        if dt is None:
            dt = try_get_datetime_from_filename(img_path)
            if dt is None:
                sys.stderr.write(
                    f"{img_path}: failed to parse datetime from filename\n"
                )
                return
            print(f"{img_path}: interpreting filename date time as {dt}")
        else:
            print(f"{img_path}: keeping existing time value {dt}")
        exif_to_append = {}
        for dttt in date_time_target_tags:
            if dttt not in exif:
                exif_to_append[dttt] = dt
        if exif_to_append:
            img_ex.modify_exif(exif_to_append)
    except (OSError, KeyError, ValueError) as ex:
        sys.stderr.write(f" {img_path}: failed to handle image: {str(ex)}\n")
    finally:
        img_ex.close()


def handle_dir(dir_rel):
    for obj in os.scandir(dir_rel):
        if obj.is_file():
            handle_image(dir_rel, obj.name)
            continue
        if obj.is_dir:
            handle_dir(os.path.join(dir_rel, obj.name))


if __name__ == "__main__":

    handle_dir(sys.argv[1])
