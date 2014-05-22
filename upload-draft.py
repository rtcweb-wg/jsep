import os
import sys
import subprocess
import shutil

print os.environ['GH_TOKEN']

if len(sys.argv) != 2:
    sys.exit(1)

built = sys.argv[1]

sys.exit(0)

os.mkdir("out")
os.chdir("out")
subprocess.check_call(["git","init","."])
shutil.move("upload-tmp", built)
subprocess.check_call(["git","add",built])
subprocess.check_call(["git","commit","-m", "Commit"])
subprocess.check_call(["git","push","origin","gh-pages"])


