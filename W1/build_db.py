"""data/*.csv → w1.db (SQLite) 적재."""
import csv, sqlite3, os
if os.path.exists("w1.db"): os.remove("w1.db")
con = sqlite3.connect("w1.db")
con.executescript(open("schema.sql", encoding="utf-8").read())
for table in ["M_ALC", "M_PN", "M_ALC_BOM", "T_SALES", "T_INVENTORY"]:
    with open(f"data/{table}.csv", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    cols = rows[0]
    con.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", rows[1:])
con.commit(); con.close()
print("w1.db built")
