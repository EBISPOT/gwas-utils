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
            
            CREATE TABLE IF NOT EXISTS last_run (
            date TEXT
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

    def insert_study(self, study: tuple) -> None:
        self.cur.execute("""
                         INSERT OR REPLACE INTO studies(
                         study,
                         harmType,
                         isHarm,
                         inProg,
                         priority)
                         VALUES (?,?,?,?,?)
                         """,
                         study)
        self.commit()

    def select_studies(self, studies: list) -> list:
        sql = f"""
               SELECT * FROM studies
               WHERE study in ({','.join(['?']*len(studies))})
               """
        self.cur.execute(sql, studies)
        data = self.cur.fetchall()
        return [self._int_to_bool(i) for i in data]

    def select_by(
        self,
        study: Union[list, None],
        harmonised_only: bool,
        harmonisation_type: list,
        limit: Union[int, None],
        in_progress: bool,
        priority: int
        ) -> list:
        args = [[harmonised_only], harmonisation_type, [in_progress], [priority]]
        conditions = ["isHarm is ?",
                      f"harmType in ({','.join(['?']*len(harmonisation_type))})",
                      "inProg is ?",
                      f"priority <= ?"]
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
        return [self._int_to_bool(i) for i in data]
    
    def last_run(self) -> Union[str, None]:
        sql = """
              SELECT date FROM last_run
              WHERE rowid = 1
              """
        self.cur.execute(sql)
        results = self.cur.fetchone()
        if len(results):
            return results[0]
        return None
    
    def reset_last_run(self, timestamp: str) -> None:
        self.cur.execute("""
                         INSERT OR REPLACE INTO last_run(
                         rowid,
                         date)
                         VALUES (?,?)
                         """,
                         (1, timestamp)
                         )
        self.commit()

    @staticmethod
    def _int_to_bool(row: tuple) -> tuple:
        return (row[0], row[1], bool(row[2]), bool(row[3]), row[4])

    def commit(self) -> None:
        self.cur.execute("COMMIT")

    def create_tables(self) -> None:
        self.cur.executescript(self.DB_SCHEMA)
