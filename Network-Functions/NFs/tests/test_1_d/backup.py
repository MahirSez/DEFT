import typer
import sys
sys.path.append('../')
from exp_package.Two_phase_commit.backup_2pc import Backup


def main(
        ip: str = typer.Option(..., '--ip', '-i', help='ip address'),
        port: str = typer.Option(..., '--port', '-p', help='port number')

):
    backup_nf = Backup(ip, int(port))
    backup_nf.listen()


if __name__ == '__main__':
    typer.run(main)
