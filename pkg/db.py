import sqlite3

from pandas import read_sql, DataFrame


class SQLite:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
    
    def get_table(self) -> DataFrame:
        return read_sql("SELECT * FROM bibliography", con=self.conn)
    
    def insert_many(self, records: list):
        cur = self.conn.cursor()
        cur.executemany("INSERT INTO bibliography values(?,?,?,?)", records)
        self.conn.commit()
    
    def close(self):
        self.conn.close()
