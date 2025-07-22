import aiohttp
from aiolimiter import AsyncLimiter
from dataclasses import dataclass

from aiohttp import ClientSession
from dacite import from_dict

limiter = AsyncLimiter(max_rate=20, time_period=1)

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

api = {
    "login": "/tiger/v3/web/accounts/login",
    "msg_count": "/web/message-record/count",
    "msg": "/web/message-record?query_type=COMMENT_REPLY&limit=5&offset=0",
    "like": "/web/forums/comments/{}/liked?source={}",
    "report": "/web/reports/posts/discussions",
    "like_work": "/nemo/v2/works/{}/like",
    "collect_work": "/nemo/v2/works/{}/collection",
    "fork_work": "/nemo/v2/works/{}/fork"
}

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
    def __init__(self):
        self.session = None
        self.verified = False
        self.token = ""
        self.id = None
        self.nickname = ""
        self.phone_number = ""

    async def login_with_token(self, token):
        self.session = aiohttp.ClientSession("https://api.codemao.cn", headers=headers)
        self.token = token
        self.session.cookie_jar.update_cookies({"authorization": self.token})
        return self

    async def login_with_identity(self, identity, password):
        self.session = aiohttp.ClientSession("https://api.codemao.cn", headers=headers)
        payload = {"identity": identity, "password": password, "pid": "65edCTyg"}
        async with self.session.post(api["login"], json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                info = from_dict(data_class=LoginInfo, data=result)
                self.verified = True
                self.id = info.user_info.id
                self.nickname = info.user_info.nickname
                self.phone_number = info.auth.phone_number
                self.token = info.auth.token
            else:
                raise LoginException("Failed to login")
            return self

    async def like_reply(self, comment_id: int):
        async with limiter:
            url = api["like"].format(comment_id, "REPLY")
            async with self.session.put(url, json={}, headers=headers) as resp:
                return resp.status == 204

    async def report_reply(self,id):
        async with limiter:
            payload = {
                "discussion_id": str(id),
                "source": "REPLY",
                "reason_id": "4",
                "description": "人身攻击"
            }
            async with self.session.post(api["report"], json=payload, headers=headers) as resp:
                return resp.status == 201

    async def like_work(self, work_id):
        async with limiter:
            url = api["like_work"].format(work_id)
            async with self.session.post(url, json={}, headers=headers) as resp:
                return resp.status == 200

    async def collect_work(self, work_id):
        async with limiter:
            url = api["collect_work"].format(work_id)
            async with self.session.post(url, json={}, headers=headers) as resp:
                return resp.status == 200

    async def fork_work(self,work_id):
        async with limiter:
            url = api["fork_work"].format(work_id)
            async with self.session.post(url, json={}, headers=headers) as resp:
                return resp.status == 200

    async def load_info(self):
        pass

    async def close(self):
        await self.session.close()

async def single_request(work_id):
    async with limiter:
        async with ClientSession(headers=headers) as session:
            async with session.head(f"https://api.codemao.cn/creation-tools/v1/works/{work_id}") as resp:
                return resp.status == 200