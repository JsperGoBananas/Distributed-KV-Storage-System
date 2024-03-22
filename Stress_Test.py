import argparse
import time

from Client import Client

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-proxy", "--proxy", help="Proxy Ip address", required=True, type=str)
    args = parser.parse_args()
    data = {}
    proxy = args.proxy
    client = Client(proxy)
    command = input("Input Command\n").upper()
    start = time.time()
    client.send_command_to_server(command.upper())
    print(f"Time: {time.time()-start}")
