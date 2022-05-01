# exif_datetime_tool
Add missing EXIF DateTime information to images based on their filenames.

## Setup
- `pip install pyexiv2`

## Usage
- Call `./exif_datetime_tool.py <directory_path>`
- This will in-place update the EXIF data of all images in `<directory_path>`,
  and it's subdirectories.
- Non Image files and files with existing DateTimes remain unchanged.
