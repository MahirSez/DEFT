import socket   
import sys
sys.path.append('../')
from exp_package.Two_phase_commit.backup_2pc import Backup
import subprocess
from subprocess import DEVNULL, STDOUT, check_call, PIPE


def get_ip_address(iface):

    # f = os.popen(f'ifconfig {iface} | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    # f = os.popen(f'ifconfig {iface} | grep "inet"')
    process = subprocess.Popen(f'ifconfig {iface} | grep "inet"', shell=True, stderr=PIPE, stdout=PIPE)
    stdout, stderr = process.communicate()
    line = stdout.decode()
    if line == "":
        return None
    your_ip = line.strip().split()[1]
    return your_ip


def main():
    # ip = 'localhost'
    # hostname=socket.gethostname()   
    # ip=socket.gethostbyname(hostname)
    interface = "eth1"

    while True:
        ip = get_ip_address(interface)
        if ip:
            break

    print(f"extracted ip is {ip}")
    port = 7000
    backup_nf = Backup(ip, port)
    backup_nf.listen()


if __name__ == '__main__':
    main()
