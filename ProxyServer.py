import argparse
import threading
import time
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as xmlrpclib
import random
import logging

key_server_dict = {}
BASE_PORT = 20000
HEARTBEAT_INTERVAL = 5
REPLICAS = 3
lock = threading.Lock()
logging.basicConfig(filename='output_proxy.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProxyServer:
    current_index = 0
    servers = []

    def function(self, clause):
        clause = clause.strip().split() 
        lens = len(clause)

        if lens < 1:
            return "Wrong input, use 'help' to get more information."

        command = clause[0]

        if command in ['PUT', 'GET', 'DELETE', 'LIST', 'LOG', 'EXIT']:
                server_function = getattr(self, command.lower())
                return server_function(clause)
        else:
            return "Wrong input, use 'help' to get more information."


    def put(self, clause):
        if len(clause) != 3:
            return 'Wrong format. Use PUT key value'

        key, value = clause[1], clause[2]

        server = self.load_balacing()
        if key in key_server_dict.keys():
            while server not in key_server_dict[key]:
                server = self.load_balacing()
        if key in key_server_dict.keys():
            delete_thead = threading.Thread(target=self.data_delete,args=key)
            delete_thead.start()
            delete_thead.join()
        with lock:
            if server.put(key, value):
                logging.info(f"Request sent to {server}")
                key_server_dict[key] = [server]
                replication = threading.Thread(target=self.data_replicate,args=(key,value))
                replication.start()
                return f"Add/Update {key}，value {value} successfully"

        return f"Fail to add/update {key}，value {value}"

    def get(self, clause):
        if len(clause) != 2:
            return 'Wrong input format, use: GET key'
        # logging.info(key_server_dict)
        key = clause[1]
        if key in key_server_dict.keys():
            s = self.load_balacing()
            while s not in key_server_dict[key]:
                s = self.load_balacing()
            logging.info(f"Request sent to {s}")
            with lock:
                value = s.get(key)
        else:
            value = None
        return f"key {key}'s value is ：{value if value is not None else '[value not found]'}"

    def list(self, clause):
        if len(clause) != 1:
            return 'Wrong input format, use: LIST'
        list = {}
        for proxy in self.servers:
                try:
                    with lock:
                        values = proxy.list()
                        list.update(values)
                except Exception as e:
                    logging.info(f"{proxy} is offline")
                    self.remove(proxy)
        return list

    def delete(self, clause):
        if len(clause) != 2:
            return 'Wrong input format, use : DELETE key'

        key = clause[1]
        if self.data_delete(key):
            return f"Delete key {key} successful"
        return f"Can not delete key {key} because it doesn't exist"


    def load_balacing(self):
        if self.current_index >= len(self.servers):
            self.current_index = (self.current_index) % len(self.servers)
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return server

    def heartbeat_thread(self):
        while True:
            for proxy in self.servers:
                    try:
                        with lock:
                            proxy.ping()
                            # logging.info(f"Heartbeat sent to{proxy}")
                    except Exception as e:
                        logging.info(f"{proxy} is Offline")
                        self.remove(proxy)
                        logging.info(f"Key_Server Mapping :")
                        logging.info("---------------------------------------")
                        for key, value in key_server_dict.items():
                            logging.info(f"{key} : {value}")
                        logging.info("---------------------------------------")
            time.sleep(HEARTBEAT_INTERVAL)

    def register(self, server_ip,database):

        logging.info(f"{server_ip} is Online")
        logging.info(f"Key_Server Mapping Before Registration:")
        logging.info("---------------------------------------")
        for key, value in key_server_dict.items():
            logging.info(f"{key} : {value}")
        logging.info("---------------------------------------")
        server = xmlrpclib.ServerProxy(f"http://{server_ip}:{BASE_PORT}")
        registration = False
        for key in database.keys():
            #服务器没有人有这个key
            if key not in key_server_dict.keys() or len(key_server_dict[key]) == 0:
                key_server_dict[key] = []
            else:
                #更新数据
                s = key_server_dict[key][0]
                value = s.get(key)
                if value != database[key]:
                    update_thread = threading.Thread(target=proxy.update,args=(server,key,value))
                    update_thread.start()
            if server not in key_server_dict[key]:
                key_server_dict[key].append(server)
        self.servers.append(server)
        for key, servers in key_server_dict.items():
            if server not in servers:
                registration = True
                s = servers[0]
                value = s.get(key)
                replication = threading.Thread(target=self.data_replicate, args=(key, value))
                replication.start()
        if(not registration):
            logging.info(f"Key_Server Mapping After Registration:")
            logging.info("---------------------------------------")
            for key,value in key_server_dict.items():
                logging.info(f"{key} : {value}")
            logging.info("---------------------------------------")
    def update(self,server,key,value):
        with lock:
            server.put(key,value)
    def remove(self,port):
        keys_to_remove = []
        for s in key_server_dict.values():
            if port in s:
                s.remove(port)
        for key in key_server_dict.keys():
            if len(key_server_dict[key]) ==0:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            key_server_dict.pop(key)
        if port in self.servers:
            self.servers.remove(port)

    def data_replicate(self,key,value):
                copies = len(key_server_dict[key])
                while copies < REPLICAS and copies!= len(self.servers):
                    server = random.choice(self.servers)
                    if server not in key_server_dict[key]:
                            with lock:
                                server.put(key, value)
                                copies+=1
                                key_server_dict[key].append(server)
                logging.info(f"After Replication:")
                logging.info("---------------------------------------")
                for key, value in key_server_dict.items():
                    logging.info(f"{key} : {value}")
                logging.info("---------------------------------------")

    def data_delete(self,key):
        if key in key_server_dict.keys():
            for server in self.servers:
                if server in key_server_dict[key]:
                    with lock:
                        server.delete(key)
            key_server_dict.pop(key)
            logging.info(key_server_dict)
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate random Traveling Sales Person problems.")
    parser.add_argument("-local", "--local", help="Local Ip address", required=True, type=str)
    args = parser.parse_args()
    local = args.local

    if not local:
        logging.info("Specify local ip address using --local 'ip' ")
        exit(0)



    proxy = ProxyServer()
    server = SimpleXMLRPCServer((local, 21000), allow_none=True)
    server.register_instance(proxy)
    heartbeat_thread = threading.Thread(target=proxy.heartbeat_thread)
    heartbeat_thread.start()
    logging.info(f"Proxy server running...")
    server.serve_forever()
