import argparse
import subprocess
import requests
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define global variables
api_url = os.getenv('api_url')
remote_file_path = os.getenv('remote_file_path')
ssh_key_path = os.getenv('ssh_key_path')

def transfer_and_notify(ssh_host, ssh_port, ssh_user, path_folder, numberPartFile, version):

    local_file_path     = path_folder+ '/'  + version + '/'+ version +  '.apk.gz_'+numberPartFile
    newRemoteFilePath   = remote_file_path  + version +  '.apk.gz_'+numberPartFile
    # Define shell command
    shell_command = f'scp -r -P {ssh_port} -i {ssh_key_path} -o "StrictHostKeyChecking no" -o ServerAliveInterval=10 -o ServerAliveCountMax=2 {local_file_path} {ssh_user}@{ssh_host}:{newRemoteFilePath}'

    result = '-'
    success = False

    # Execute shell command
    try:
        result = subprocess.run(shell_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(result)
        if result.returncode == 0:
            result = f"File transfer successful: {newRemoteFilePath}"
            print(result)
            success = True
        else:
            result = f"File transfer failed: {newRemoteFilePath}. Error message: {result.stderr}"
            print(result)
    except subprocess.CalledProcessError as e:
        result = f"Error transferring file {newRemoteFilePath}: {e}"
        print(result)

    # Send message to API
    api_data = {'message': f'Transfer of {local_file_path} to {ssh_host} completed successfully', 'result': result, 'success': success}
    api_headers = {'Authorization': f'Bearer 939608268'}
    try:
        response = requests.post(api_url, data=api_data, headers=api_headers)
        response.raise_for_status()
        print(f"API request successful. Response: {response.text}")
        if response.status_code != 200:
            print(f'Error sending message to API: {response.status_code} {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")

def checkRootFolder(ssh_host):
     # Check if destination folder exists and create it if it doesn't exist
    folder_name = os.path.dirname(remote_file_path)
    ssh_check_folder_command = f'ssh -p 22 -i {ssh_key_path} -o "StrictHostKeyChecking no" root@{ssh_host} "test -d {folder_name} || mkdir -p {folder_name}"'
    try:
        result = subprocess.run(ssh_check_folder_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print(f"Folder check successful: {folder_name}")
        else:
            print(f"Error checking folder {folder_name}: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error checking folder {folder_name}: {e}")
    

def main(args):
    # Check if destination folder exists and create it if it doesn't exist
    checkRootFolder(args.ssh_host)

    for numberPartFile in args.file_paths:
        try:
            transfer_and_notify(args.ssh_host, args.ssh_port, args.ssh_user, args.path_folder, numberPartFile, args.version)
        except Exception as e:
            print(f"Error transferring file: {e}")

if __name__ == '__main__':
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='Transfer binary files over SSH using scp and send message to API')
    parser.add_argument('--ssh_host', type=str, required=True, help='SSH host')
    parser.add_argument('--ssh_port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--ssh_user', type=str, default='root', help='SSH username')
    parser.add_argument('--path_folder', type=str, required=True, help='Path to work folder')
    parser.add_argument('--file_paths', type=str, nargs='+', required=True, help='List of paths to local for concat files')
    parser.add_argument('--version', type=str, required=True, help='Version to APK')
    args = parser.parse_args()

    main(args)
