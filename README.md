git-annex-photo-import
======================

A script to import photos into git-annex and munge some useful metadata into them.

    import.py annex-dir files-to-import

Imports files and adds git-annex metadata from EXIF. It also queries the Google geolocation
API to attach readable place names as metadata. The way it chooses from its location name 
options and names the metadata fields is currently a heuristic that will work best in the U.S.

It renames the files to include the date & time as well as the
original filename, and uppercases all the file extensions so that
git-annex will spot files with duplicate contents but different
extensions as duplicates.

It puts all the files in one directory, and assumes that you will use
metadata and annex views to create any hierarchy you want.

It also currently uses a /tmp directory (change it via the STAGING_DIR
env var) to stage files, so that importing doesn't modify the original
files.

## Requirements

It currently requires the python module
[ExifRead](https://pypi.python.org/pypi/ExifRead), although an earlier
version used exiftool, and most of the code to support that is still
there, waiting on reintegration.

## Example

Here's the metadata the script added to an iPhone picture of mine:

```
% git annex metadata 2011-12-02_18:31:52-IMG_1161.JPG
metadata 2011-12-02_18:31:52-IMG_1161.JPG 
  Address=8800 Burnet Road, Austin, TX 78757, USA
  Code=78757
  Country=United States
  County=Travis County
  DateTimeOriginal=2011:12:02 18:31:52
  Day=2
  GPSAltitude=328243/1428
  GPSAltitudeRef=0
  GPSImgDirection=9857/1162
  GPSImgDirectionRef=T
  GPSLatitude=[30, 556/25, 0]
  GPSLatitudeRef=N
  GPSLongitude=[97, 873/20, 0]
  GPSLongitudeRef=W
  Locality=Austin
  Model=iPhone 4
  Month=12
  Neighborhood=North Shoal Creek
  Route=Burnet Road
  SourceFile=/Volumes/Four TB Backup/Mike's iPhone 4 backup/IMG_1161.JPG
  State=Texas
  Year=2011
```

This metadata allows you to do nice things with git-annex views like this:

```
% git annex view "Year=*" "Month=*"

% ls -l 2011/12/*
lrwxr-xr-x  1 mmccrack  staff   204B Aug  4 07:43 2011-12-02_18:31:52-IMG_1161.JPG -> ../../.git/annex/objects/gp/Wz/SHA256E-s1617420--96cd231aeab6f53379eb7ee7ecc6153f78132deec47cbaf795c572281654ecd1.JPG/SHA256E-s1617420--96cd231aeab6f53379eb7ee7ecc6153f78132deec47cbaf795c572281654ecd1.JPG
```

## Caveats 

Note that you currently have to do the final 'git commit' yourself
after running the import script.

