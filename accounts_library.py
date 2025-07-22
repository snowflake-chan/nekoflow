import asyncio
import sqlite3
from user import User
from tqdm.asyncio import tqdm_asyncio

class AccountManager:
    def __init__(self, lib=".db"):
        """
        Initialize the account manager
        :param lib: Path to the sqlite3 database
        """
        self.con = sqlite3.connect(lib)
        self.cur = self.con.cursor()
        self._create_table()

    def _create_table(self):
        """ Create the table if it doesn't exist """

        table_sql = """
        CREATE TABLE IF NOT EXISTS accounts (
            is_ticked INTEGER NOT NULL,
            id INTEGER PRIMARY KEY,
            identity TEXT,
            nickname TEXT,
            password TEXT,
            token TEXT,
            has_phone_number INTEGER NOT NULL,
            comments TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.cur.execute(table_sql)
        self.con.commit()

        trigger_sql = """
        CREATE TRIGGER IF NOT EXISTS update_timestamp
        AFTER UPDATE ON accounts
        FOR EACH ROW
        BEGIN
            UPDATE accounts SET last_updated = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """
        self.cur.execute(trigger_sql)
        self.con.commit()

    async def add_account(self,identity,password):
        user = User()
        try:
            user = await user.login_with_identity(identity,password)
            has_phone_number = user.phone_number != ""
            self.cur.execute("INSERT INTO accounts(is_ticked,id,identity,nickname,password,"
                             "token,has_phone_number,comments,last_updated)"
                             "VALUES (0,?,?,?,?,?,?,'',CURRENT_TIMESTAMP);",
                             (user.id, identity, user.nickname, password, user.token, has_phone_number))
            self.con.commit()
            print(f"Successfully added {user.nickname}({user.id}) to the collection.")
        except Exception as e:
            await user.close()
            self.con.rollback()
            print(e)

    def get_collection(self):
        """ From page get nicknames of the collection """

        self.cur.execute("SELECT id, nickname, is_ticked FROM accounts ORDER BY is_ticked DESC;")
        return self.cur.fetchall()

    def get_collection_count(self):
        self.cur.execute("SELECT COUNT(*) FROM accounts;")
        return self.cur.fetchone()[0]

    def tick(self, target):
        param = [(id,) for id in target]
        self.cur.execute("UPDATE accounts SET is_ticked = 0 where is_ticked = 1;")
        self.cur.executemany("UPDATE accounts SET is_ticked = 1 WHERE id = ?;", param)
        self.con.commit()

    async def get_ticked(self):
        self.cur.execute("SELECT token FROM accounts WHERE is_ticked=1 ORDER BY is_ticked DESC;")
        u = UserSet()
        await u.register((i[0] for i in self.cur.fetchall()))
        return u

class UserSet:
    def __init__(self):
        self.user_set = set()

    async def register(self,tokens):
        resp = await asyncio.gather(*(User().login_with_token(t) for t in tokens))
        self.user_set.update(resp)

    async def like_reply(self, reply_id):
        l = (u.like_reply(reply_id) for u in self.user_set)
        await self.gather(l)

    async def report_reply(self, reply_id):
        l = (u.report_reply(reply_id) for u in self.user_set)
        await self.gather(l)

    async def like_work(self, work_id):
        l = (u.like_work(work_id) for u in self.user_set)
        await self.gather(l)

    async def collect_work(self, work_id):
        l = (u.collect_work(work_id) for u in self.user_set)
        await self.gather(l)

    async def fork_work(self, work_id):
        l = (u.fork_work(work_id) for u in self.user_set)
        await self.gather(l)

    async def follow(self, user_id):
        l = (u.follow(user_id) for u in self.user_set)
        await self.gather(l)

    async def gather(self, l):
        resp = await tqdm_asyncio.gather(*l)
        succeeded = resp.count(True)
        total = len(self.user_set)
        print(f"{succeeded} / {total} OK")
        await self.close()

    async def close(self):
        await asyncio.gather(*(u.close() for u in self.user_set))