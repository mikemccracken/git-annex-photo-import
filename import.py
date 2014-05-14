#! python3

from collections import defaultdict
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time

#TODO py3.3 uses shlex.quote
from pipes import quote

USE_STAGING = True              # rename into temp dir

WANTED_KEYS = ['CreateDate', 'GPSLongitude', 'GPSLongitudeRef', 'GPSLatitude', 'GPSLatitudeRef', 'ImageDescription', 'Model', 'Year', 'Month', 'Day', 'SourceFile', 'GPSImgDirection', 'GPSImgDirectionRef', 'GPSAltitude', 'GPSAltitudeRef']
# for reference while hacking:
ALL_KEYS = ['YResolution', 'GPSImgDirectionRef', 'ResolutionUnit', 'FilePermissions', 'GPSLongitude', 'Make', 'SourceFile', 'FlashpixVersion', 'SceneCaptureType', 'ThumbnailImage', 'SubjectArea', 'Directory', 'YCbCrPositioning', 'XResolution', 'GPSPosition', 'Aperture', 'Compression', 'GPSAltitudeRef', 'GPSTimeStamp', 'BitsPerSample', 'GPSImgDirection', 'ModifyDate', 'LightValue', 'ExposureProgram', 'ShutterSpeed', 'ShutterSpeedValue', 'ColorSpace', 'FocalLength35efl', 'ExifImageWidth', 'ThumbnailOffset', 'DateTimeOriginal', 'ImageWidth', 'ThumbnailLength', 'CreateDate', 'MIMEType', 'SensingMethod', 'FNumber', 'Flash', 'ApertureValue', 'FocalLength', 'FileType', 'ImageDescription', 'ComponentsConfiguration', 'ExifByteOrder', 'FileAccessDate', 'ExifImageHeight', 'ImageHeight', 'EncodingProcess', 'FileInodeChangeDate', 'Model', 'ExifToolVersion', 'GPSLongitudeRef', 'YCbCrSubSampling', 'Software', 'ExposureTime', 'Orientation', 'MeteringMode', 'GPSLatitude', 'Sharpness', 'GPSLatitudeRef', 'ColorComponents', 'FileName', 'WhiteBalance', 'GPSAltitude', 'FileSize', 'FileModifyDate', 'ExposureMode', 'ImageSize', 'ISO', 'DigitalZoomRatio', 'ExifVersion']

logging.basicConfig(filename='git-annex-photo-import.log', level=logging.DEBUG)


def timestruct_from_metadata(m):
    datetimestr = m["CreateDate"]
    timestruct = time.strptime(datetimestr, "%Y:%m:%d %H:%M:%S") 
    return timestruct

def filename_from_metadata(m):
    sourcefilename = m["SourceFile"]
    ignore, extension = os.path.splitext(sourcefilename)
    timestruct = timestruct_from_metadata(m)
    filename = time.strftime("%H:%M:%S-%B-%d-%Y", timestruct)
    return filename + extension
    
def import_files(filenames):
    if len(filenames) == 0:
        return False
    # TODO: calling import per file is less efficient but helps with
    # errors. is there a better way?

    for filename in filenames:
        try:
            logging.info("importing {}".format(filename))
            cmd = "git-annex import '{}'".format(filename)
            out = subprocess.check_output(cmd, shell=True, 
                                          stderr=subprocess.STDOUT,
                                          env=os.environ) # TODO: hack for PATH
            logging.info("- success")
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and "not overwriting existing" in e.output:
                logging.warn("- skipping existing file.")
            else:
                logging.error("error in import: {code}\noutput:\n{output}".format(code=e.returncode, output=e.output))
                logging.info("stopping import.")
                return False
    
def add_metadata_to_imported_file(m):
    addmdcmd = "git -c annex.alwayscommit=false annex metadata \"{fname}\" -s \"{key}={value}\" --quiet"

    for k,v in m.items():

        if k not in WANTED_KEYS: continue

        try:
            fn = m["filename_for_git_annex"]
            cmd = addmdcmd.format(fname=fn, key=quote(str(k)), value=quote(str(v)))
            logging.debug("\t - " + cmd)
            out = subprocess.check_output(cmd, shell=True,                                    
                                          stderr=subprocess.STDOUT,
                                          env=os.environ) # TODO: hack for PATH
        except subprocess.CalledProcessError as e:
            logging.error("error in add_metadata_to_imported_file:"
                  "{code}\noutput:\n{output}".format(code=e.returncode, output=e.output))
            return False

# TODO:
# - set metadata for place name using google apis: http://maps.googleapis.com/maps/api/geocode/json?latlng=53.244921,-4.479539&sensor=true


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: import.py [destination annex path] filename(s)")
        sys.exit(1)
    annexpath = sys.argv[1]
    os.chdir(annexpath)
    
    if USE_STAGING:
        staging_dir = tempfile.mkdtemp("git-annex-import", dir="/tmp")
        logging.info("using staging dir ={}".format(staging_dir))
    else:
        staging_dir = ""

    files_to_import = []

    filenames = " ".join(sys.argv[2:])

    jstr = subprocess.check_output("exiftool -json {}".format(filenames), shell=True)
    raw_mlist = json.loads(jstr)

    mlist = [defaultdict(lambda: "unknown", **m_raw) for m_raw in raw_mlist]

    for m in mlist:
        source_file_name = m['SourceFile']
        m["filename_for_git_annex"] = filename_from_metadata(m)
        filename_for_git_annex = os.path.join(staging_dir, m["filename_for_git_annex"])
        if USE_STAGING:
            logging.info("copying {} to {}".format(source_file_name, filename_for_git_annex))
            shutil.copy2(source_file_name, filename_for_git_annex)
        else:
            logging.info("moving {} to {}".format(source_file_name, filename_for_git_annex))
            shutil.move(source_file_name, filename_for_git_annex)

        files_to_import.append(filename_for_git_annex)
        
    success = import_files(files_to_import)
    if success == False:
        # todo: remove temp dir?
        logging.error("errors importing files. exiting.")
        sys.exit()

    for m in mlist:
        ts = timestruct_from_metadata(m)

        m.update(dict(Year=ts.tm_year,
                  Month=ts.tm_mon,
                  Day=ts.tm_mday))

        add_metadata_to_imported_file(m)
            
    if staging_dir != "":
        logging.debug("removing {}".format(staging_dir))
        shutil.rmtree(staging_dir)
