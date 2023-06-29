from typing import Union
from pathlib import Path
import sqlite3
import itertools


class SqliteClient():
    """
    Minimal sqlite3 client.
    """
    DB_SCHEMA = """
            CREATE TABLE IF NOT EXISTS studies (
            study TEXT NOT NULL UNIQUE,
            harmType TEXT,
            isHarm BOOL,
            inProg BOOL,
            priority INT
            );
            """
            
    def __init__(self, database: Path) -> None:
        self.database = database
        self.conn = self.create_conn()
        self.cur = self.conn.cursor()
        if self.conn:
            self.create_tables()

    def create_conn(self) -> Union[sqlite3.Connection, None]:
        try:
            conn = sqlite3.connect(self.database)
            conn.row_factory = sqlite3.Row
            return conn
        except NameError as e:
            print(e)
        return None

    def insert_new_study(self, study: tuple) -> None:
        self.cur.execute("""
                         INSERT OR IGNORE INTO studies(
                         study,
                         harmType,
                         isHarm,
                         inProg,
                         priority)
                         VALUES (?,?,?,?,?)
                         """,
                         study)
        self.commit()
        
    def select_by(
        self,
        study: Union[list, None],
        harmonised_only: bool,
        harmonisation_type: list,
        limit: Union[int, None],
        in_progress: bool,
        priority: list
        ) -> list:
        args = [[harmonised_only], harmonisation_type, [in_progress], priority]
        conditions = ["isHarm is ?",
                      f"harmType in ({','.join(['?']*len(harmonisation_type))})",
                      "inProg is ?",
                      f"priority in ({','.join(['?']*len(priority))})"]
        sql = f"""
               SELECT * FROM studies
               WHERE
               {" AND ".join(conditions)}
               """
        if study:
            sql += f" AND study in ({','.join(['?']*len(study))})"
            args.append(study)
        flattened_args = list(itertools.chain.from_iterable(args))
        self.cur.execute(sql, flattened_args)
        data = self.cur.fetchmany(size=limit)
        return [tuple(i[0],bool(i[1]),i[2], bool(i[3]), i[4]) for i in data]

    def commit(self) -> None:
        self.cur.execute("COMMIT")

    def create_tables(self) -> None:
        self.cur.executescript(self.DB_SCHEMA)
