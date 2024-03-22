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
    data_size = input("Input Command\n").upper()
    start = time.time()
    for i in range(int(data_size)):
        client.send_command_to_server(f"delete {i}".upper())
    print(f"Time: {time.time()-start}")