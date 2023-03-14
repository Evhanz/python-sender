eval "$(ssh-agent -s)"
ssh-add /path/to/your/private/key


## for install in mode ofline 
pip3 install --no-index --find-links=my-packages argparse subprocess requests python-dotenv


## for install in online mode 
pip3 install argparse subprocess requests python-dotenv

## Example exec 
python3 transferv_2.py --ssh_host 192.168.3.252 --path_folder /Users/Eidelman.Hernandez/Documents/ms4m/pythonsend --file_paths c4mobile-release-2023.07a18.apk.gz_00 --version c4mobile-release-2023.07a18