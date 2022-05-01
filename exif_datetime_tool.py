#!/usr/bin/env python3

from PIL import Image, ExifTags, UnidentifiedImageError
import datetime
import re
import sys
import os
import glob
from typing import Optional


EXIF_TAG_STRINGS = {v: k for (k, v) in ExifTags.TAGS.items()}
date_time_source_tags = [
    EXIF_TAG_STRINGS["DateTime"],
    EXIF_TAG_STRINGS["DateTimeOriginal"],
    EXIF_TAG_STRINGS["DateTimeDigitized"],
]
# we set the gathered information on all three of these,
# because different tools use different things ...
date_time_target_tags = date_time_source_tags


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


for img in glob.glob(input_path + "/**.jp*"):
    try:
        img_pil = Image.open(img)
    except (OSError, UnidentifiedImageError) as ex:
        sys.stderr.write(f"{img}: failed to open image: {str(ex)}\n")
        continue
    try:
        img_exif = img_pil.getexif()
        for dtst in date_time_source_tags:
            dt = img_exif.get(dtst, None)
            if dt is not None:
                break
        if dt is None:
            dt = try_get_datetime_from_filename(img)
            if dt is None:
                print(f"{img}: failed to parse datetime from filename")
                continue
            print(f"{img}: interpreting filename date time as {dt}")
        else:
            print(f"{img}: keeping existing time value {dt}")
        for dttt in date_time_target_tags:
            if dttt not in img_exif:
                img_exif[dttt] = dt
        img_pil.save(
            os.path.join(output_path, os.path.basename(img)),
            exif=img_exif
        )
    except (OSError, KeyError, ValueError) as ex:
        sys.stderr.write(f"failed to handle image: {img}: {str(ex)}\n")
    finally:
        img_pil.close()
