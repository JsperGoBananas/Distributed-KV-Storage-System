import argparse
import xmlrpc.client as xmlrpclib

class Client(object):
    def __init__(self, proxy_ip):
        self.proxy = xmlrpclib.ServerProxy(f'http://{proxy_ip}:21000', allow_none=True)
        self.port = None


    def handle_user_command(self):
        try:
            while True:
                command = input(f"Please enter your command (PUT/GET/DELETE/LIST/EXIT)>> ").upper()
                if command == 'HELP':
                    self.print_help()
                else:
                    if command == 'EXIT':
                        break
                    self.send_command_to_server(command)

        except KeyboardInterrupt:
            pass

    def print_help(self):

        print(
            "-------------------------------------------\n"
            "Commands:\n"
            "PUT key value —— Add (key, value)\n"
            "GET key —— Get key's value\n"
            'DELETE key —— Delete key \n'
            'LIST —— List all (key, value)\n'
            'EXIT —— Exit Client\n'
            "-------------------------------------------"
        )

    def send_command_to_server(self, command):
        msg = getattr(self.proxy, 'function')(command)
        if msg is not None:
            print(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate random Traveling Sales Person problems.")
    parser.add_argument("-proxy", "--proxy", help="Proxy Ip address", required=True, type=str)

    args = parser.parse_args()

    proxy = args.proxy


    if not proxy:
        print("Specify proxy ip address using --proxy 'ip'")
        exit(0)
    client = Client(proxy)
    print('-------------------------------------------')
    print('Welcome')
    print("Enter 'help' to get command list。")
    print('-------------------------------------------')
    client.handle_user_command()
