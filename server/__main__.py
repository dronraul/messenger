import yaml
import json
import select
import logging
from socket import socket
from argparse import ArgumentParser

from protocol import validate_request, make_response
from handlers import handle_default_request
from resolvers import resolve


parser = ArgumentParser()

parser.add_argument(
    '-c', '--config', type=str,
    required=False, help='Sets config file path'
)

args = parser.parse_args()

default_config = {
    'host': 'localhost',
    'port': 8000,
    'buffersize': 1024
}

if args.config:
    with open(args.config) as file:
        file_config = yaml.load(file, Loader=yaml.Loader)
        default_config.update(file_config)

host, port = (default_config.get('host'), default_config.get('port'))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

requests = []
connections = []

try:
    sock = socket()
    sock.bind((host, port,))
    sock.settimeout(0)
    sock.listen(5)

    logging.info(f'Server was started with {host}:{port}')

    while True:
        try:
            client, address = sock.accept()

            connections.append(client)

            logging.info(f'Client was connected with {address[0]}:{address[1]} | Connections: {connections}')
        except :
            pass

        try:
            rlist, wlist, xlist = select.select(
                connections, connections, connections, 0
            )

            for r_client in rlist:
                b_request = r_client.recv(default_config.get('buffersize'))
                requests.append(b_request)

            if requests:
                b_request = requests.pop()
                b_response = handle_default_request(b_request)

                for w_client in wlist:
                    w_client.send(b_response)
        except OSError:
            pass



except KeyboardInterrupt:
    logging.info('Server shutdown')