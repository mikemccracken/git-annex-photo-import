git-annex-photo-import
======================

A script to import photos into git-annex and munge some useful metadata into them.

    import.py annex-dir files-to-import

Imports files and adds git-annex metadata from EXIF. It also queries the Google geolocation
API to attach readable place names as metadata. The way it chooses from its location name 
options and names the metadata fields is currently a heuristic that will work best in the U.S.

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
