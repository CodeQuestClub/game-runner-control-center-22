import os
import shutil
import pysftp

# Variables
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
host= 'fs-cil.easywp.com'
username= 'codequest-447769'
password = 'AjvYR49DXdtdC-75oesI'
input_dir = 'raw_submissions/'
output_dir = "submissions/"

shutil.rmtree(input_dir)
shutil.rmtree(output_dir)
os.makedirs(input_dir)
os.makedirs(output_dir)


#Connecting to server and downloading the content of "user_uploads" to "input_dir"

with pysftp.Connection(host= host, username=username, password=password, cnopts=cnopts) as sftp:
    sftp.cwd('/wp-content/uploads/user_uploads')
    sftp.get_r('.', input_dir , preserve_mtime=True)


list_of_directories = os.listdir(input_dir)
for username_dir in list_of_directories:
    list_of_files = sorted(filter(lambda x: os.path.isfile(os.path.join(input_dir,username_dir, x)),
                                  os.listdir(os.path.join(input_dir,username_dir))))
    if list_of_files:
        latest_file = list_of_files[-1]
        shutil.copy(os.path.join(input_dir,username_dir,latest_file), output_dir+username_dir+".zip")
    else:
        continue