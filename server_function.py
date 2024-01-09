import pykka


# サーバー側の基本的な機能についての関数
class ServerBasicFunction(pykka.ThreadingActor):
    def __init__(self):
        super(ServerBasicFunction, self).__init__()

    # 通信先がクライアントだけ
    def registration_client(self, instance_name1, instance_name2):
        self.TrueClient_ref = instance_name1
        self.Attacker_ref = instance_name2

    # 通信先がクライアントとリストサーバー
    def registration_client_and_key_array(self, instance_name1, instance_name2, instance_name3):
        self.TrueClient_ref = instance_name1
        self.Attacker_ref = instance_name2
        self.WordList_ref = instance_name3

    # どのユーザーから何サーバーが呼ばれたか表示
    @staticmethod
    def notification(name, type):
        print("")
        print(name + "から" + type + "サーバーの呼び出しを検知")

    # 鍵の照合
    @staticmethod
    def key_judge(key, collect_key):
        if (key == collect_key):
            return True
        else:
            print("認証できません")
            return False

    # 名前に対する文字列照合
    @staticmethod
    def name_judge(name, collect_name):
        if (name == collect_name):
            return True
        else:
            print("認証できません")
            return False

    # 足し算、認証成功すると動く関数
    @staticmethod
    def add(num1, num2):
        print(str(num1) + "と" + str(num2) + "の加算")
        print("結果は" + str(num1 + num2))

    # アクセス元へ同じトークンを返すようにする
    def return_token(self, name, token):
        if (name == "user"):
            self.TrueClient_ref.tell({"order": "token_renew",
                                      "token": token})
        elif (name == "attacker"):
            self.Attacker_ref.tell({"order": "token_renew",
                                    "token": token})

    # アクセス元へ同じ文字列を返すようにする
    def return_word(self, name, word):
        if (name == "user"):
            self.TrueClient_ref.tell({"order": "challenge",
                                      "word": word})
        elif (name == "attacker"):
            self.Attacker_ref.tell({"order": "challenge",
                                    "word": word})

    # WordListに対してリクエストを送る
    def request_wordlist(self, name):
        self.WordList_ref.tell({"order": "request",
                                "name": name})

