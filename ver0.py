import logging
import random
import pykka
import time

class TrueClient(pykka.ThreadingActor):
    def __init__(self,token):
        super(TrueClient,self).__init__()
        print("clientアクター起動")
        self.token=token
        print("Client's initial token: "+str(self.token))

    def link_class(self,instance_name):
        self.Server_ref=instance_name

    def on_receive(self,message):
        self.message=message
        if(self.message["order"]=="access"):
            self.num1=random.randint( 1,1000)
            self.num2=random.randint(1,1000)
            self.Server_ref.tell({"order":"add",
                                  "name":"user",
                                  "key":self.token,
                                  "num1":self.num1,
                                  "num2":self.num2})
        elif(self.message["order"]=="renew"):
            self.token=self.message["token"]
            print("Client's new token: " + str(self.token))



class Attacker(pykka.ThreadingActor):
    def __init__(self,token):
        super(Attacker,self).__init__()
        print("Attackerアクター起動")
        self.token=token
        print("Attacker's initial token: "+str(self.token))

    def link_class(self,instance_name):
        self.Server_ref=instance_name

    def on_receive(self,message):
        self.message=message
        if (self.message["order"] == "access"):
            self.num1=random.randint(1,1000)
            self.num2=random.randint(1,1000)
            self.Server_ref.tell({"order":"add",
                                  "name":"attacker",
                                  "key":self.token,
                                  "num1":self.num1,
                                  "num2":self.num2})
            self.token=random.randint(1,10000000000)
            print("Attacker's new token: " + str(self.token))
        elif (self.message["order"] == "renew"):
            self.token = self.message["token"]
            print("Attacker's new token: " + str(self.token))


class Server(pykka.ThreadingActor):
    def __init__(self,token):
        super(Server,self).__init__()
        print("serverアクター起動")
        self.token = token
        print("Server's initial token: "+str(self.token))

    def link_class(self,instance_name1,instance_name2):
        self.TrueClient_ref = instance_name1
        self.Attacker_ref = instance_name2

    def on_receive(self,message):
        self.message = message
        print("")
        print(self.message["name"]+"からサーバーの呼び出しを検知")
        # 渡されたトークンの一致不一致で条件分岐
        if (self.token==self.message["key"]):
            print("トークンが一致")
            if(self.message["order"]=="add"):
                print(str(self.message["num1"])+"と"+str(self.message["num2"])+"の加算")
                print("結果は"+str(self.message["num1"]+self.message["num2"]))
            # 新しいトークンへの更新
            self.new_token = random.randint(1, 10000000000)
            print("Server's new token: " + str(self.new_token))
            self.token = self.new_token
            # アクセスされたところへ同じトークンを返すようにする
            if(self.message["name"]=="user"):
                self.TrueClient_ref.tell({"order":"renew",
                                          "token":self.token})
            elif(self.message["name"]=="attacker"):
                self.Attacker_ref.tell({"order":"renew",
                                        "token":self.token})

        else:
            print("トークンが違います")

def main():

    logging.basicConfig(level=logging.DEBUG)
    # アクターの起動、トークンの初期値を与える
    TrueClient_ref = TrueClient.start(3)
    Attacker_ref = Attacker.start(random.randint(1,10000000000))
    Server_ref = Server.start(3)

    # プロキシ設定
    TrueClient_proxy = TrueClient_ref.proxy()
    Attacker_proxy = Attacker_ref.proxy()
    Server_proxy = Server_ref.proxy()

    # 通信するアクターの設定
    TrueClient_proxy.link_class(Server_ref)
    Attacker_proxy.link_class(Server_ref)
    Server_proxy.link_class(TrueClient_ref,Attacker_ref)

    # とりあえず5回の試行
    for num in range(5):
        # 変数の数合わせでテキトーなトークン入れてるがorder:accessの時トークンは更新されない
        TrueClient_ref.tell({"order":"access",
                             "token":1})
        time.sleep(5)
        Attacker_ref.tell({"order":"access",
                             "token":1})
        time.sleep(5)
        Attacker_ref.tell({"order":"access",
                             "token":1})
        time.sleep(5)

    TrueClient_ref.stop()
    Attacker_ref.stop()
    Server_ref.stop()

if __name__ == '__main__':
    main()
