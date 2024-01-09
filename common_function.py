import random
import pykka
import hashlib
import string


# クライアント、サーバー両方で出番がある(かもしれない)機能についての関数
class CommonFunction(pykka.ThreadingActor):
    def __init__(self):
        super(CommonFunction, self).__init__()

    # 初期トークンを設定する関数
    def set_initial_token(self, name, token):
        self.token = token
        print(name + "'s initial token: " + str(self.token))

    def set_initial_password(self, name, password):
        self.password = password
        print(name + "'s initial password: " + str(self.password))

    # ユーザーのトークン認証失敗/サーバー側のトークン更新
    def token_renew_random(self, name):
        self.new_token = random.randint(1, 10000000000)
        print(name + "'s new token: " + str(self.new_token))
        return self.new_token

    # 文字列のハッシュ化
    def word_hash(self, word):
        self.hash_word = hashlib.sha256(word.encode()).hexdigest()
        print(self.hash_word)
        return self.hash_word

    # numの長さのランダム文字列を返す関数
    def get_random_string(self, num):
        self.random_string = ''.join(random.choices(string.ascii_letters, k=num))
        return self.random_string
