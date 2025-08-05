import aiohttp
from aiolimiter import AsyncLimiter
from dataclasses import dataclass

from aiohttp import ClientSession
from dacite import from_dict
from asyncio import Semaphore

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
    "fork_work": "/nemo/v2/works/{}/fork",
    "follow": "/nemo/v2/user/{}/follow"
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
        self.limiter = AsyncLimiter(max_rate=20, time_period=1)
        self.semaphore = Semaphore(50)

    async def _request(self, method, url, **kwargs):
        async with self.limiter:
            async with self.semaphore:
                async with getattr(self.session, method)(url, **kwargs) as resp:
                    return resp

    async def login_with_token(self, token):
        self.session = aiohttp.ClientSession("https://api.codemao.cn", headers=headers)
        self.token = token
        self.session.cookie_jar.update_cookies({"authorization": self.token})
        return self

    async def login_with_identity(self, identity, password):
        self.session = aiohttp.ClientSession("https://api.codemao.cn", headers=headers)
        payload = {"identity": identity, "password": password, "pid": "65edCTyg"}
        resp = await self._request("post", api["login"], json=payload, headers=headers)
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
        url = api["like"].format(comment_id, "REPLY")
        resp = await self._request("put", url, json={}, headers=headers)
        return resp.status == 204

    async def report_reply(self, id):
        payload = {
            "discussion_id": str(id),
            "source": "REPLY",
            "reason_id": "4",
            "description": "人身攻击"
        }
        resp = await self._request("post", api["report"], json=payload, headers=headers)
        return resp.status == 201

    async def like_work(self, work_id):
        url = api["like_work"].format(work_id)
        resp = await self._request("post", url, json={}, headers=headers)
        return resp.status == 200

    async def collect_work(self, work_id):
        url = api["collect_work"].format(work_id)
        resp = await self._request("post", url, json={}, headers=headers)
        return resp.status == 200

    async def fork_work(self, work_id):
        url = api["fork_work"].format(work_id)
        resp = await self._request("post", url, json={}, headers=headers)
        return resp.status == 200

    async def follow(self, user_id):
        url = api["follow"].format(user_id)
        resp = await self._request("post", url, json={}, headers=headers)
        return resp.status == 204

    async def load_info(self):
        pass

    async def close(self):
        if self.session:
            await self.session.close()

async def single_request(work_id):
    limiter = AsyncLimiter(max_rate=20, time_period=1)
    semaphore = Semaphore(50)
    async with semaphore:
        async with limiter:
            async with ClientSession(headers=headers) as session:
                async with session.head(f"https://api.codemao.cn/creation-tools/v1/works/{work_id}") as resp:
                    return resp.status == 200