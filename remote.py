import secrets
import sys

import Remote

from unet.flag import FlagParser, PositionalFlag, OptionFlag, Group

__all__ = ["remote-simple"]

REMOTE_FLAGS = {
    "host": PositionalFlag(
        help="host to connect to (default: 0.0.0.0)",
        nargs="?",
        type=str,
        default="0.0.0.0",
    ),
    "port": PositionalFlag(
        help="port to connect to (default: random)",
        nargs="?",
        type=int,
        default=secrets.randbelow(0xffff),
    ),
    "ipv6": OptionFlag(
        short="-6",
        long="--ip6",
        help="use IPv6",
        action="store_true",
        required=False,
        default=False,
    ),
    "listen": OptionFlag(
        short="-l",
        long="--listen",
        help="listen for incoming connections (default: connect)",
        action="store_true",
        required=False,
        default=False,
    ),
    "udp": OptionFlag(
        short="-u",
        long="--udp",
        help="use UDP (default: TCP)",
        action="store_true",
        required=False,
        default=False,
    ),
    "command": OptionFlag(
        short="-c",
        long="--command",
        help="command shell",
        action="store_true",
        required=False,
        default=False,
    ),
    "execute": OptionFlag(
        short="-e",
        long="--execute",
        help="execute the supplied command",
        type=str,
        required=False,
        default=None,
        metavar="<cmd>",
    ),
    "upload": OptionFlag(
        short="-o",
        help="upload the supplied file",
        type=str,
        required=False,
        default=None,
        metavar="<in file>",
    ),
    "examples": Group(
        description="\n".join([
            "unet remote-simple 192.168.1.108 5555 -l -c    # command shell",
            "unet remote-simple 192.168.1.108 5555 -l -u file.txt   # upload to file",
            "unet remote-simple 192.168.1.108 5555 -l -e cat /etc/passwd    # execute a command",
            "echo 'ABC' | unet remote-simple 192.168.1.108 135      # echo text to server port 135",
            "unet remote-simple # connect to 0.0.0.0 with random port",
        ]),
        arguments={},
    ),
}


def main(args: list[str]) -> None:
    parser = FlagParser(
        prog='remote-simple', description='make or wait for remote connections')
    parser.add_arguments(REMOTE_FLAGS)
    flags = parser.parse_args(args)

    if flags.listen:
        print(f"listening on {flags.target}:{flags.port}")
        buffer = ''
    else:
        print(f"connect to {flags.target}:{flags.port}")
        buffer = sys.stdin.read()

    remote = Remote(flags, buffer.encode())
    remote.start()