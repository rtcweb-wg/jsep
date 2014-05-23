import os
import sys
import subprocess
import shutil

if len(sys.argv) != 2:
    sys.exit(1)

built = sys.argv[1]

os.mkdir("out")
os.chdir("out")
subprocess.check_call(["git","init","."])
subprocess.check_call(["git","config","--global","user.email","ekr-cibot@rtfm.com"])
subprocess.check_call(["git","config","--global","user.name","EKR CI Bot"])
shutil.move("../%s"%built, ".")
subprocess.check_call(["git","add",built])
subprocess.check_call(["git","commit","-m", "Commit"])
subprocess.check_output(["git","push","--force","https://${GH_TOKEN}@${GH_REF}","master:gh-pages"], stderr=subprocess.STDOUT)


