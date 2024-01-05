import logging
import random
import pykka
import time


class TrueClient(pykka.ThreadingActor):
    def __init__(self, token):
        super(TrueClient, self).__init__()
        print("clientアクター起動")
        self.token = token
        print("Client's initial token: " + str(self.token))

    def link_class(self, instance_name, instance_name2):
        self.Server_Type_Token_ref = instance_name
        self.Server_Type_Onetime1_ref = instance_name2

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "token_access"):
            self.num1, self.num2 = givenum()
            self.Server_Type_Token_ref.tell({"order": "add",
                                  "name": "user",
                                  "key": self.token,
                                  "num1": self.num1,
                                  "num2": self.num2})
        elif (self.message["order"] == "token_renew"):
            self.token = self.message["token"]
            print("Client's new token: " + str(self.token))
        elif (self.message["order"] == "Onetime1_access"):
            self.num1, self.num2 = givenum()
            self.Server_Type_Onetime1_ref.tell({"order": "add",
                                  "name": "user",
                                  "key": self.message["pass"],
                                  "num1": self.num1,
                                  "num2": self.num2})

class Attacker(pykka.ThreadingActor):
    def __init__(self, token):
        super(Attacker, self).__init__()
        print("Attackerアクター起動")
        self.token = token
        print("Attacker's initial token: " + str(self.token))

    def link_class(self, instance_name, instance_name2):
        self.Server_Type_Token_ref = instance_name
        self.Server_Type_Onetime1_ref = instance_name2

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "token_access"):
            self.num1, self.num2 = givenum()
            self.Server_Type_Token_ref.tell({"order": "add",
                                  "name": "attacker",
                                  "key": self.token,
                                  "num1": self.num1,
                                  "num2": self.num2})
            self.token = random.randint(1, 10000000000)
            print("Attacker's new token: " + str(self.token))
        elif (self.message["order"] == "token_renew"):
            self.token = self.message["token"]
            print("Attacker's new token: " + str(self.token))
        elif (self.message["order"] == "Onetime1_access"):
            self.num1, self.num2 = givenum()
            self.Server_Type_Onetime1_ref.tell({"order": "add",
                                  "name": "attacker",
                                  "key": self.message["pass"],
                                  "num1": self.num1,
                                  "num2": self.num2})


# 各サーバーの共通的な機能になりそうな部分
class Common_Server(pykka.ThreadingActor):
    def __init__(self):
        super(Common_Server, self).__init__()

    def link_class(self, instance_name1, instance_name2):
        self.TrueClient_ref = instance_name1
        self.Attacker_ref = instance_name2

    #足し算するだけ
    def add(self, num1, num2):
        print(str(num1) + "と" + str(num2) + "の加算")
        print("結果は" + str(num1 + num2))

class Server_Type_Token(Common_Server, pykka.ThreadingActor):
    def __init__(self, token):
        super(Server_Type_Token, self).__init__()
        print("Server_Type_Tokenアクター起動")
        self.token = token
        print("Server_Type_Token's initial token: " + str(self.token))

    def on_receive(self, message):
        self.message = message
        notification(self.message["name"], "トークン")
        # 渡されたトークンの一致不一致で条件分岐
        if (self.token == self.message["key"]):
            print("トークンが一致")
            if (self.message["order"] == "add"):
                super().add(self.message["num1"],self.message["num2"])
            # 新しいトークンへの更新
            self.new_token = random.randint(1, 10000000000)
            print("Server_Type_Token's new token: " + str(self.new_token))
            self.token = self.new_token
            # アクセスされたところへ同じトークンを返すようにする
            if (self.message["name"] == "user"):
                self.TrueClient_ref.tell({"order": "token_renew",
                                          "token": self.token})
            elif (self.message["name"] == "attacker"):
                self.Attacker_ref.tell({"order": "token_renew",
                                        "token": self.token})
        else:
            print("トークンが違います")

# きわめて簡素な実装,1回しか使えない
class Server_Type_Onetime1(Common_Server, pykka.ThreadingActor):
    def __init__(self, password):
        super(Server_Type_Onetime1, self).__init__()
        print("Server_Type_Onetime1アクター起動")
        self.password = password
        print("Server_Type_Onetime1's password: " + str(self.password))

    def on_receive(self, message):
        self.message = message
        notification(self.message["name"],"ワンタイム1")
        if (self.password == self.message["key"]):
            if (self.message["name"] == "user"):
                print("ワンタイムパスワードおよび所有者の一致")
                if (self.message["order"] == "add"):
                    super().add(self.message["num1"], self.message["num2"])
                # 新しいパスワードへの更新、1回だけ使用が前提なのでユーザーに返す通信をしない
                self.password = random.randint(1, 10000000000)
            else:
                print("認証できません")
        else:
            print("認証できません")


def givenum():
    return random.randint(1, 1000), random.randint(1, 1000)


def notification(name, type):
    print("")
    print(name + "から" + type + "サーバーの呼び出しを検知")


def main():

    logging.basicConfig(level=logging.DEBUG)
    # アクターの起動、トークンの初期値を与える
    TrueClient_ref = TrueClient.start(3)
    Attacker_ref = Attacker.start(random.randint(1,10000000000))
    Common_Server_Type_Token_ref = Common_Server.start()
    Server_Type_Token_ref = Server_Type_Token.start(3)
    Server_Type_Onetime1_ref = Server_Type_Onetime1.start(1000000)

    # プロキシ設定
    TrueClient_proxy = TrueClient_ref.proxy()
    Attacker_proxy = Attacker_ref.proxy()
    Common_Server_Type_Token_proxy = Common_Server_Type_Token_ref.proxy()
    Server_Type_Token_proxy = Server_Type_Token_ref.proxy()
    Server_Type_Onetime1_proxy = Server_Type_Onetime1_ref.proxy()

    # 通信するアクターの設定
    TrueClient_proxy.link_class(Server_Type_Token_ref, Server_Type_Onetime1_ref)
    Attacker_proxy.link_class(Server_Type_Token_ref, Server_Type_Onetime1_ref)
    Server_Type_Token_proxy.link_class(TrueClient_ref, Attacker_ref)
    Server_Type_Onetime1_proxy.link_class(TrueClient_ref, Attacker_ref)

    time.sleep(5)

    # ワンタイム側、ユーザー名違いの弾きとパスワード更新できてることの確認
    Attacker_ref.tell({"order": "Onetime1_access",
                         "pass": 1000000})
    time.sleep(5)
    TrueClient_ref.tell({"order": "Onetime1_access",
                         "pass": 1000000})
    time.sleep(5)
    Attacker_ref.tell({"order": "Onetime1_access",
                       "pass": 1000000})

    time.sleep(5)
    # とりあえず5回の試行
    for num in range(5):
        TrueClient_ref.tell({"order": "token_access"})
        time.sleep(5)
        Attacker_ref.tell({"order": "token_access"})
        time.sleep(5)
        Attacker_ref.tell({"order": "token_access"})
        time.sleep(5)

    TrueClient_ref.stop()
    Attacker_ref.stop()
    Server_Type_Token_ref.stop()
    Common_Server_Type_Token_ref.stop()
    Server_Type_Onetime1_ref.stop()

if __name__ == '__main__':
    main()