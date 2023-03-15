import argparse
import paramiko
import base64

def main(args):
    # Load private key
    ssh_key = paramiko.RSAKey.from_private_key_file(args.ssh_key_path)

    # Connect to SSH server
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=args.ssh_host, port=args.ssh_port, username=args.ssh_user, pkey=ssh_key)

    # Open transport
    transport = ssh_client.get_transport()
    channel = transport.open_session()

    # Send file
    channel.exec_command('echo "$(</dev/stdin)" | base64 -d > {}'.format(args.remote_file_path))
    with open(args.local_file_path, 'rb') as f:
        data = base64.b64encode(f.read())
        channel.sendall(data)

    # Close transport and SSH connection
    channel.shutdown_write()
    channel.close()
    transport.close()
    ssh_client.close()

if __name__ == '__main__':
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='Transfer binary files over SSH')
    parser.add_argument('--ssh_host', type=str, required=True, help='SSH host')
    parser.add_argument('--ssh_port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--ssh_user', type=str, required=True, help='SSH username')
    parser.add_argument('--ssh_key_path', type=str, required=True, help='Path to SSH private key')
    parser.add_argument('--local_file_path', type=str, required=True, help='Path to local binary file')
    parser.add_argument('--remote_file_path', type=str, required=True, help='Path to remote binary file')
    args = parser.parse_args()



    main(args)
