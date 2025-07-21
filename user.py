from requests import Session
from dataclasses import dataclass
from dacite import from_dict

src = "https://api.codemao.cn"

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

api = {
    "login": "/tiger/v3/web/accounts/login",
    "msg_count": "/web/message-record/count",
    "msg": "/web/message-record?query_type=COMMENT_REPLY&limit=5&offset=0",
    "like": "/web/forums/comments/{}/liked?source={}"
}

def get_url(key):
    return src + api[key]

@dataclass
class AuthInfo:
    token: str
    phone_number: str
    email: str
    has_password: bool
    is_weak_password: bool

@dataclass
class UserInfo:
    id: int
    nickname: str
    avatar_url: str
    fullname: str
    birthday: int
    sex: int
    qq: str
    description: str
    grade: int
    grade_desc: str

@dataclass
class LoginInfo:
    auth: AuthInfo
    user_info: UserInfo

class LoginException(Exception):
    pass

class User:
    verified: bool = False

    id:int
    nickname:str
    phone_number:str
    token: str

    def __init__(self, *args):
        self.session = Session()
        self.session.headers.update(headers)
        if len(args) == 1:
            self.session.cookies.update({"authorization": args[0]})
        elif len(args) == 2:
            identity, password = args
            d = self.session.post(get_url("login"),
                              json={"identity": identity, "password": password, "pid": "65edCTyg"})
            if d.status_code == 200:
                info = from_dict(data_class=LoginInfo, data=d.json())
                self.verified = True
                self.id = info.user_info.id
                self.nickname = info.user_info.nickname
                self.phone_number = info.auth.phone_number
                self.token = info.auth.token
            else:
                raise LoginException("Failed to login")

    def load_info(self):
        pass

    def like_reply(self, id):
        self.session.put(get_url("like").format(id,"REPLY"),"{}")