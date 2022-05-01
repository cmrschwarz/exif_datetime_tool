# exif_datetime_tool
Add missing EXIF DateTime information to images based on their filenames.

## Setup
- `pip install pyexiv2`

## Usage
- place (a copy of) the images you want to process in a directory (`directory_path`)
- calling `./exif_datetime_tool.py directory_path` will update the exif data of the images (in place!)
