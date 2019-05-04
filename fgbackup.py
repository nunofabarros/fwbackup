#!/usr/bin/env python3
import paramiko
import getpass
from scp import SCPClient
from datetime import datetime
import sys

cmd_enable_scp = """
config system global

set admin-scp enable

end
exit
"""

cmd_disable_scp = """
config system global
    unset admin-scp
end
exit
"""


def get_fw(fws='firewalls.conf'):
    servers = []
    file = open(fws, 'r')
    for line in file.readlines():
        if len(line) > 0:
            servers.append(line.strip())
    return servers


def run_fw_command(fw, username, password, cmd):
    print('Connecting to server {} with username {}'.format(fw, username))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(fw, username=username, password=password)
        ssh.exec_command(cmd)
    except paramiko.ssh_exception.SSHException as ex:
        print(ex)


def backup_config(fw, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(fw, username=username, password=password)
    scp = SCPClient(ssh.get_transport())
    scp.get('sys_config',  'backup/{}_{}.config'.format(fw.replace('.', '_'), datetime.now().isoformat()))


def start(args):
    if len(args) == 0:
        firewalls = get_fw()
    elif len(args) == 1:
        firewalls = get_fw(args[0])
    else:
        print("Invalid arguments")
        sys.exit(0)
    username = input("Username: <{}>\n".format(getpass.getuser()))
    if len(username) <= 0:
        username = getpass.getuser()
    password = getpass.getpass("Password: \n")

    for fw in firewalls:
        run_fw_command(fw, username, password, cmd_enable_scp)
        backup_config(fw, username, password)
        run_fw_command(fw, username, password, cmd_disable_scp)


if __name__ == '__main__':
    start(sys.argv[1:])
