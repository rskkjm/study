import random
import pykka


# クライアント側の基本的な機能についての関数
class ClientBasicFunction(pykka.ThreadingActor):
    def __init__(self):
        super(ClientBasicFunction, self).__init__()

    # 通信するサーバーを登録する関数
    def registration_server(self, instance_name, instance_name2, instance_name3):
        self.ServerTypeToken_ref = instance_name
        self.ServerTypeOnetimeOne_ref = instance_name2
        self.ServerTypeOnetimeTwo_ref = instance_name3

    # キーを添えて送るメッセージを生成する関数
    def send_message_with_key(self, order, name, key, server_type):
        self.num1, self.num2 = random.randint(1, 1000), random.randint(1, 1000)
        if (server_type == "token"):
            self.ServerTypeToken_ref.tell({"order": order,
                                           "name": name,
                                           "key": key,
                                           "num1": self.num1,
                                           "num2": self.num2})
        elif (server_type == "onetime1"):
            self.ServerTypeOnetimeOne_ref.tell({"order": order,
                                                "name": name,
                                                "key": key,
                                                "num1": self.num1,
                                                "num2": self.num2})
        elif (server_type == "onetime2"):
            self.ServerTypeOnetimeTwo_ref.tell({"order": order,
                                                "name": name,
                                                "key": key,
                                                "num1": self.num1,
                                                "num2": self.num2})

    # キーを添えずに送るメッセージを生成する関数
    def send_message_without_key(self, order, name, server_type):
        if (server_type == "onetime2"):
            self.ServerTypeOnetimeTwo_ref.tell({"order": order,
                                                "name": name})

    # トークン認証成功時のトークン更新
    def token_renew_when_success(self, name, token):
        self.new_token = token
        print(name + "'s new token: " + str(self.new_token))
        return self.new_token
