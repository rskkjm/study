import logging
import random
import pykka
import time
import common_function
import client_function
import server_function


class TrueClient(common_function.CommonFunction, client_function.ClientBasicFunction, pykka.ThreadingActor):
    def __init__(self, token):
        super(TrueClient, self).__init__()
        print("Clientアクター起動")
        super().set_initial_token("user", token)

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "token_access"):
            super().send_message_with_key("add", "user", self.token, "token")
        elif (self.message["order"] == "token_renew"):
            self.token = super().token_renew_when_success("user", self.message["token"])
        elif (self.message["order"] == "Onetime1_access"):
            super().send_message_with_key("add", "user", self.message["pass"], "onetime1")
        elif (self.message["order"] == "Onetime2_access"):
            super().send_message_without_key("request", "user", "onetime2")
        elif (self.message["order"] == "challenge"):
            self.hash_string = super().word_hash(self.message["word"])
            super().send_message_with_key("add", "user", self.hash_string, "onetime2")


class Attacker(common_function.CommonFunction, client_function.ClientBasicFunction, pykka.ThreadingActor):
    def __init__(self, token):
        super(Attacker, self).__init__()
        print("Attackerアクター起動")
        super().set_initial_token("attacker", token)

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "token_access"):
            super().send_message_with_key("add", "attacker", self.token, "token")
            time.sleep(5)
            self.token = super().token_renew_random("attacker")
        elif (self.message["order"] == "token_renew"):
            self.token = super().token_renew_when_success("attacker", self.message["token"])
        elif (self.message["order"] == "Onetime1_access"):
            super().send_message_with_key("add", "attacker", self.message["pass"], "onetime1")
        elif (self.message["order"] == "Onetime2_access"):
            super().send_message_without_key("request", "attacker", "onetime2")
        elif (self.message["order"] == "challenge"):
            # ハッシュ渡しを知らないのでそのまま返す仮定
            self.string = self.message["word"]
            super().send_message_with_key("add", "attacker", self.string, "onetime2")


class ServerTypeToken(common_function.CommonFunction, server_function.ServerBasicFunction, pykka.ThreadingActor):
    def __init__(self, token):
        super(ServerTypeToken, self).__init__()
        print("ServerTypeTokenアクター起動")
        super().set_initial_token("ServerTypeToken", token)

    def on_receive(self, message):
        self.message = message
        super().notification(self.message["name"], "トークン")
        # 渡されたトークンの一致不一致で条件分岐
        if (super().key_judge(self.message["key"], self.token)):
            print("トークンの一致")
            if (self.message["order"] == "add"):
                super().add(self.message["num1"], self.message["num2"])
            # 新しいトークンへの更新
            self.token = super().token_renew_random("ServerTypeToken")
            # アクセス元へ同じトークンを返すようにする
            super().return_token(self.message["name"], self.token)


# きわめて簡素な実装,1回しか使えない
class ServerTypeOnetimeOne(common_function.CommonFunction, server_function.ServerBasicFunction, pykka.ThreadingActor):
    def __init__(self, password):
        super(ServerTypeOnetimeOne, self).__init__()
        print("ServerTypeOnetimeOneアクター起動")
        super().set_initial_password("ServerTypeOnetimeOne", password)

    def on_receive(self, message):
        self.message = message
        super().notification(self.message["name"], "ワンタイム1")
        if (super().key_judge(self.message["key"], self.password)):
            if (super().name_judge(self.message["name"], "user")):
                print("ワンタイムパスワードおよび所有者の一致")
                if (self.message["order"] == "add"):
                    super().add(self.message["num1"], self.message["num2"])
                # 新しいパスワードへの更新、1回だけ使用が前提なのでユーザーに返す通信をしない
                self.password = random.randint(1, 10000000000)


class ServerTypeOnetimeTwo(common_function.CommonFunction, server_function.ServerBasicFunction, pykka.ThreadingActor):
    def __init__(self):
        super(ServerTypeOnetimeTwo, self).__init__()
        print("ServerTypeOnetimeTwoアクター起動")

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "request"):
            #
            super().notification(self.message["name"], "ワンタイム2")
            super().request_wordlist(self.message["name"])
            time.sleep(5)
        elif (self.message["order"] == "set"):
            self.word = self.message["word"]
            print(self.word)
            # リクエスト元へ文字列を返す
            super().return_word(self.message["name"], self.word)
        elif (self.message["order"] == "add"):
            self.answer = super().word_hash(self.word)
            if (super().key_judge(self.message["key"], self.answer)):
                if (super().name_judge(self.message["name"], "user")):
                    print("ワンタイムパスワードおよび所有者の一致")
                    if (self.message["order"] == "add"):
                        super().add(self.message["num1"], self.message["num2"])
            self.WordList_ref.tell({"order": "move"})


# ハッシュ列の元になるランダム文字列のリストを生成しリクエストに応じてひとつ返すサーバー
class WordList(common_function.CommonFunction, pykka.ThreadingActor):
    def __init__(self, flag, point):
        super(WordList, self).__init__()
        self.flag = flag
        self.point = point

    def link_server(self, instance_name):
        self.ServerTypeOnetimeTwo_ref = instance_name

    def generate_array(self):
        self.key_array = ["a"] * 1000
        for i in range(1000):
            self.key_array[i] = super().get_random_string(10)
        print(self.key_array)

    def move_point(self):
        for i in range(100):
            self.point = random.randint(1, 999)
            if (self.flag == 0):
                break

    def on_receive(self, message):
        self.message = message
        if (self.message["order"] == "request"):
            self.flag = 0
            self.ServerTypeOnetimeTwo_ref.tell({"order": "set",
                                                "name": self.message["name"],
                                                "word": self.key_array[self.point]})
            time.sleep(5)
        elif (self.message["order"] == "move"):
            self.flag = 1
            self.move_point()
        elif (self.message["order"] == "stop"):
            self.flag = 0


def main():

    logging.basicConfig(level=logging.DEBUG)
    # アクターの起動、トークンの初期値を与える
    TrueClient_ref = TrueClient.start(3)
    Attacker_ref = Attacker.start(random.randint(1, 10000000000))
    ServerTypeToken_ref = ServerTypeToken.start(3)
    ServerTypeOnetimeOne_ref = ServerTypeOnetimeOne.start(1000000)
    ServerTypeOnetimeTwo_ref = ServerTypeOnetimeTwo.start()
    WordList_ref = WordList.start(1, random.randint(1, 999))

    # プロキシ設定
    TrueClient_proxy = TrueClient_ref.proxy()
    Attacker_proxy = Attacker_ref.proxy()
    ServerTypeToken_proxy = ServerTypeToken_ref.proxy()
    ServerTypeOnetimeOne_proxy = ServerTypeOnetimeOne_ref.proxy()
    ServerTypeOnetimeTwo_proxy = ServerTypeOnetimeTwo_ref.proxy()
    WordList_proxy = WordList_ref.proxy()

    # 通信するアクターの設定
    TrueClient_proxy.registration_server(ServerTypeToken_ref, ServerTypeOnetimeOne_ref, ServerTypeOnetimeTwo_ref)
    Attacker_proxy.registration_server(ServerTypeToken_ref, ServerTypeOnetimeOne_ref, ServerTypeOnetimeTwo_ref)
    ServerTypeToken_proxy.registration_client(TrueClient_ref, Attacker_ref)
    ServerTypeOnetimeOne_proxy.registration_client(TrueClient_ref, Attacker_ref)
    ServerTypeOnetimeTwo_proxy.registration_client_and_key_array(TrueClient_ref, Attacker_ref, WordList_ref)
    WordList_proxy.link_server(ServerTypeOnetimeTwo_ref)

    WordList_proxy.generate_array()

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
    for num in range(5):
        Attacker_ref.tell({"order": "Onetime2_access"})
        time.sleep(10)
        TrueClient_ref.tell({"order": "Onetime2_access"})
        time.sleep(10)
        Attacker_ref.tell({"order": "Onetime2_access"})
        time.sleep(10)

    # とりあえず5回の試行
    for num in range(5):
        TrueClient_ref.tell({"order": "token_access"})
        time.sleep(5)
        Attacker_ref.tell({"order": "token_access"})
        time.sleep(5)
        Attacker_ref.tell({"order": "token_access"})
        time.sleep(5)

    WordList_ref.tell({"order": "stop"})
    time.sleep(3)

    TrueClient_ref.stop()
    Attacker_ref.stop()
    ServerTypeToken_ref.stop()
    ServerTypeOnetimeOne_ref.stop()
    ServerTypeOnetimeTwo_ref.stop()
    WordList_ref.stop()


if __name__ == '__main__':
    main()