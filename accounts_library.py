import sqlite3
from user import User

class AccountManager:
    def __init__(self, lib=".db"):
        """
        Initialize the account manager
        :param lib: Path to the sqlite3 database
        """
        self.con = sqlite3.connect(lib)
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
        self.con.execute(table_sql)
        self.con.commit()

        trigger_sql = """
        CREATE TRIGGER IF NOT EXISTS update_timestamp
        AFTER UPDATE ON accounts
        FOR EACH ROW
        BEGIN
            UPDATE accounts SET last_updated = CURRENT_TIMESTAMP WHERE uid = OLD.uid;
        END;
        """
        self.con.execute(trigger_sql)
        self.con.commit()

    def add_account(self,identity,password):
        user = User(identity,password)
        has_phone_number = user.phone_number is not None
        self.con.execute("INSERT INTO accounts(is_ticked,id,identity,nickname,password,token,has_phone_number,comments,last_updated)"
                         "VALUES (0,?,?,?,?,?,?,'',CURRENT_TIMESTAMP);",
                         (user.id, identity, user.nickname, password, user.token, has_phone_number))
        self.con.commit()
