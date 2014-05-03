#! python3

from collections import defaultdict
import os
import json
import subprocess
import sys
import shutil
import time
import tempfile

USE_STAGING = True              # rename into temp dir

WANTED_KEYS = ['CreateDate', 'GPSLongitude', 'GPSLatitude', 'ImageDescription', 'Model']
# for reference while hacking:
ALL_KEYS = ['YResolution', 'GPSImgDirectionRef', 'ResolutionUnit', 'FilePermissions', 'GPSLongitude', 'Make', 'SourceFile', 'FlashpixVersion', 'SceneCaptureType', 'ThumbnailImage', 'SubjectArea', 'Directory', 'YCbCrPositioning', 'XResolution', 'GPSPosition', 'Aperture', 'Compression', 'GPSAltitudeRef', 'GPSTimeStamp', 'BitsPerSample', 'GPSImgDirection', 'ModifyDate', 'LightValue', 'ExposureProgram', 'ShutterSpeed', 'ShutterSpeedValue', 'ColorSpace', 'FocalLength35efl', 'ExifImageWidth', 'ThumbnailOffset', 'DateTimeOriginal', 'ImageWidth', 'ThumbnailLength', 'CreateDate', 'MIMEType', 'SensingMethod', 'FNumber', 'Flash', 'ApertureValue', 'FocalLength', 'FileType', 'ImageDescription', 'ComponentsConfiguration', 'ExifByteOrder', 'FileAccessDate', 'ExifImageHeight', 'ImageHeight', 'EncodingProcess', 'FileInodeChangeDate', 'Model', 'ExifToolVersion', 'GPSLongitudeRef', 'YCbCrSubSampling', 'Software', 'ExposureTime', 'Orientation', 'MeteringMode', 'GPSLatitude', 'Sharpness', 'GPSLatitudeRef', 'ColorComponents', 'FileName', 'WhiteBalance', 'GPSAltitude', 'FileSize', 'FileModifyDate', 'ExposureMode', 'ImageSize', 'ISO', 'DigitalZoomRatio', 'ExifVersion']


def filename_from_metadata(m):
    sourcefilename = m["SourceFile"]
    ignore, extension = os.path.splitext(sourcefilename)
    
    datetimestr = m["CreateDate"]
    datestr, timestr = datetimestr.split(" ")
    year, month, day = datestr.split(":")
    timestruct = time.strptime(datetimestr, "%Y:%m:%d %H:%M:%S") 
    filename = time.strftime("%H:%M:%S-%B-%d-%Y")
    return filename + extension
    
def import_files(filenames):
    if len(filenames) == 0:
        return False
    try:
        print("importing files: {}".format(" ".join(filenames)))
        out = subprocess.check_output("git-annex import {}".format(" ".join(filenames)),
                                      env=os.environ) # TODO: hack for PATH
        return True
    except subprocess.CalledProcessError as e:
        print("error in import: {code}\noutput:\n{output}".format(code=e.code, output=e.output))
        return False
    
def add_metadata_to_imported_file(m):
    addmdcmd = "git -c annex.alwayscommit=false annex metadata {fname} -s '{key}={value}' --quiet"
    for k,v in m:
        if k not in WANTED_KEYS: continue

        try:
            fn = m["filename_for_git_annex"]
            out = subprocess.check_output(addmdcmd.format(fname=fn, key=k, value=v),
                                          env=os.environ) # TODO: hack for PATH
            return True
        except subprocess.CalledProcessError as e:
            print("error in import: {code}\noutput:\n{output}".format(code=e.code, output=e.output))
            return False

# TODO:
# - set metadata for year, month, day
# - set metadata for place name using google apis: http://maps.googleapis.com/maps/api/geocode/json?latlng=53.244921,-4.479539&sensor=true


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: import.py [destination annex path] filename(s)")
        sys.exit(1)
    annexpath = sys.argv[1]
    os.chdir(annexpath)
    
    if USE_STAGING:
        staging_dir = tempfile.mkdtemp("git-annex-import", dir="/tmp")
        print("using staging dir ={}".format(staging_dir))
    else:
        staging_dir = ""

    files_to_import = []

    filenames = " ".join(sys.argv[2:])

    jstr = subprocess.check_output("exiftool -json {}".format(filenames), shell=True)
    mlist = json.loads(jstr)
    for m_raw in mlist:
        m = defaultdict(lambda : "unknown")
        m.update(m_raw)
        source_file_name = m['SourceFile']
        print("\nimporting " + source_file_name)
        m["filename_for_git_annex"] = filename_from_metadata(m)
        filename_for_git_annex = os.path.join(staging_dir, m["filename_for_git_annex"])
        print(" rename to " + filename_for_git_annex)
        if USE_STAGING:
            shutil.copy2(source_file_name, filename_for_git_annex)
        else:
            shutil.move(source_file_name, filename_for_git_annex)
        files_to_import.append(filename_for_git_annex)
        
    success = import_files(files_to_import)
    if success == False:
        # todo: remove temp dir?
        sys.exit()

    for m in mlist:
        add_metadata_to_imported_file(m)
    
        
    # todo remove temp dir