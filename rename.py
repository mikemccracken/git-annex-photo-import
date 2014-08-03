
import glob
import logging
import os
import sys
import subprocess
import time

logging.basicConfig(filename='git-annex-photo-rename.log', level=logging.INFO)

filenames = []
for pat in ['*.JPG', '*.jpg', '*.MOV', '*.mov', '*.THM', '*.thm']:
    filenames += glob.glob(pat)


for filename in filenames:
    name, ext = os.path.splitext(filename)
    namepart = ""
    try:
        datepart = name
        if 'IMG' in datepart:
            datepart = name[:name.index("-IMG")]
            namepart = name[name.index("-IMG"):]
        orig_struct = time.strptime(datepart, "%H:%M:%S-%B-%d-%Y")
    except ValueError:
        logging.warning("can not parse date in '{}', skipping.".format(filename))
        continue

    newstr = time.strftime("%Y-%m-%d_%H:%M:%S", orig_struct)
    newext = ext.upper()
    newname = newstr + namepart + ext
    cmds = ["git", "mv", filename, newname]
    try:
        logging.info("running {}".format(str(cmds)))
        out = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
        print(out)
    except subprocess.CalledProcessError as e:
        logging.error("error running git cmd: {}\noutput:{}".format(e.returncode, e.output))

print("Done, don't forget to commit")
