import logging
import socket
import pykka

class Client(pykka.ThreadingActor):
    def __init__(self):
        super(Client,self).__init__()
        print("clientアクター起動")
    def link_class(self, instance_name):
        self.Server_ref = instance_name
    def connect_c(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((socket.gethostname(),9999))
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        msg=s.recv(4096)
        print(msg.decode("utf-8"))

class Server(pykka.ThreadingActor):
    def __init__(self):
        super(Server,self).__init__()
        print("serverアクター起動")
    def link_class(self, instance_name):
        self.Client_ref = instance_name
    def connect_s(self):
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((socket.gethostname(),9999))
        s.listen(10)
        while True:
            clientsocket,address=s.accept()
            print("{address}からの接続を確立")
            clientsocket.send(bytes("hello world",'utf-8'))
            clientsocket.close()



def main():

    logging.basicConfig(level=logging.DEBUG)
    # アクターの起動
    Client.ref=Client.start()
    Server.ref=Server.start()

    # プロキシ設定
    Client_proxy=Client.ref.proxy()
    Server_proxy=Server.ref.proxy()

    # 通信するアクターの登録
    Client_proxy.link_class(Server.ref)
    Server_proxy.link_class(Client.ref)

    # クライアントとサーバーの接続
    Client_proxy.connect_c()
    Server_proxy.connect_s()


if __name__ == '__main__':
    main()