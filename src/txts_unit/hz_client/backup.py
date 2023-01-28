import socket   
import sys
sys.path.append('../')
from exp_package.Two_phase_commit.backup_2pc import Backup


def main():
    # ip = 'localhost'
    hostname=socket.gethostname()   
    ip=socket.gethostbyname(hostname)
    print(f"extracted ip is {ip}")
    port = 7000
    backup_nf = Backup(ip, port)
    backup_nf.listen()


if __name__ == '__main__':
    main()
