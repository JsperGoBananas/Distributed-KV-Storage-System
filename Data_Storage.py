import argparse
import json

from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as xmlrpclib
# 这里模拟数据库
database = {}
# 数据持久化
filename = "database.json"
BASE_PORT = 20000
PROXY_PORT = 21000
# 尝试打开文件进行读取
try:
    with open(filename, "r") as file:
        database = json.load(file)
except FileNotFoundError:
        database = {}

class Server:
    def __init__(self,proxy):
        self.proxy_server = xmlrpclib.ServerProxy(f'http://{proxy}:{PROXY_PORT}')
    def put(self, key, value):
        # 存储键值对到数据库并更新缓存
        database[key] = value
        with open("database.json","w") as f:
            json.dump(database, f, ensure_ascii=False, default=lambda o: o.__dict__)
        return True

    def get(self, key):
        value = database.get(key)
        return value

    def delete(self, key):
        if key in database:
            del database[key]
            with open("database.json", "w") as f:
                json.dump(database, f, ensure_ascii=False, default=lambda o: o.__dict__)
            return True
        return False

    def list(self):
        # 返回整个数据库
        return database


    def ping(self):
        return 1
def run_server(local,proxy):
    # 启动和运行 XML-RPC 服务器
    server = SimpleXMLRPCServer((local, BASE_PORT), requestHandler=SimpleXMLRPCRequestHandler, allow_none=True)
    print(server)
    server.register_instance(Server(proxy))
    print(f"Server {local} operating on port: {BASE_PORT}\n")
    # Register to Naming_server
    register(local,proxy)
    server.serve_forever()

def register(local,proxy):
    proxy_server = xmlrpclib.ServerProxy(f'http://{proxy}:{PROXY_PORT}')
    proxy_server.register(local,database)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate random Traveling Sales Person problems.")
    parser.add_argument("-local", "--local", help="Local Ip address", required=True, type=str)
    parser.add_argument("-proxy", "--proxy", help="Proxy Ip address", required=True, type=str)

    args = parser.parse_args()

    local = args.local
    proxy = args.proxy


    if not local:
        print("Specify local ip address using --local 'ip'")
        exit(0)

    if not proxy:
        print("Specify local ip address using --proxy 'ip'")
        exit(0)



    run_server(local,proxy)
