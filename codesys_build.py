import sys
import os

args = sys.argv[1].split("|")
svn_url = args[0]
local_path = args[1]
project_name = args[2]
svn_user = args[3] if len(args) > 3 else ""
svn_pass = args[4] if len(args) > 4 else ""
output_dir = args[5] if len(args) > 5 else local_path + "\\output"
output_path = output_dir.rstrip("\\/") + "\\Application.app"

if not os.path.isdir(local_path):
    os.makedirs(local_path)
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

if svn_user and svn_pass:
    def provide_credentials(url, realm, username, may_save):
        return svn_user, svn_pass, True
    svn.auth_username_password += provide_credentials

svn.checkout(svn_url, local_path, project_name)
proj = projects.primary
app = proj.active_application

app.build()
app.create_boot_application(output_path)

proj.close()
sys.exit(0)
