import argparse
import paramiko
import requests
import os

# Define global variables
api_url = 'https://your-api.com/message'
remote_file_path = '/sdcard/c4mobile/'
ssh_key_path = '/Users/Eidelman.Hernandez/Documents/ms4m/pythonsend/system_key.bin'
ssh_password = 'mssadminkey2018'

def transfer_and_notify(ssh_host, ssh_port, ssh_user, path_folder, numberPartFile, version):
    local_file_path     = path_folder+ '/'  + version + '/'+ version +  '.apk.gz_'+numberPartFile
    newRemoteDilePath   = remote_file_path  + version +  '.apk.gz_'+numberPartFile
    
    # Create SSH client and load key
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, key_filename=ssh_key_path, password=ssh_password)

    # Create SFTP client
    sftp = ssh.open_sftp()

    # Transfer file to remote server
    try:
        sftp.put(local_file_path, newRemoteDilePath)
        print(f"File transfer successful: {newRemoteDilePath}")
    except Exception as e:
        print(f"Error transferring file {newRemoteDilePath}: {e}")
        return

    # Send message to API
    api_data = {'message': f'Transfer of {local_file_path} to {ssh_host} completed successfully'}
    api_headers = {'Authorization': f'Bearer 939608268'}
    try:
        response = requests.post(api_url, data=api_data, headers=api_headers)
        response.raise_for_status()
        print(f"API request successful. Response: {response.text}")
        if response.status_code != 200:
            print(f'Error sending message to API: {response.status_code} {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")

    # Close SFTP and SSH connections
    sftp.close()
    ssh.close()

def checkRootFolder(ssh_host):
    # Check if destination folder exists and create it if it doesn't exist
    folder_name = os.path.dirname(remote_file_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname=ssh_host, port=22, username='root', key_filename=ssh_key_path, password=ssh_password)
    sftp = ssh.open_sftp()
    try:
        sftp.stat(folder_name)
        print(f"Folder check successful: {folder_name}")
    except FileNotFoundError:
        sftp.mkdir(folder_name)
        print(f"Folder {folder_name} created.")
    except Exception as e:
        print(f"Error checking folder {folder_name}: {e}")
        return
    finally:
        sftp.close()
        ssh.close()
    

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
