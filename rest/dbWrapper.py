import sqlite3
import pandas as pd

# This the dbManager class acts as a wrapper for the database.
# This class will create custom queries to the database, process and return the result.

class dbManager(): 
    def __init__(self):
        self.conn = sqlite3.connect('names_database.db', check_same_thread=False)
        self.cur = self.conn.cursor()


    def get_name(self, name):
        query = f"""select * from ssa_names where name like \"{name}\";"""
        # self.cur.execute()
        return pd.read_sql(query, con=self.conn).to_json(orient="records")

    
if __name__ == "__main__":
    db = dbManager()
    res = db.get_name("veronica")
    print(res)
