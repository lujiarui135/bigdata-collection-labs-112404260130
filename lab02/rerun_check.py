# -*- coding: utf-8 -*-
"""独立重跑：关闭上次程序后，另起一个进程再次执行入库，验证不会重复插入。"""
import csv
from pathlib import Path

import pymysql

FIELDS = ["title", "house", "address", "struct", "area", "floor", "maketime", "price"]
DB_CONFIG = {
    "host": "mysql", "port": 3306, "database": "smartpark_lab",
    "user": "student", "password": "123456", "charset": "utf8mb4", "autocommit": False,
}
INSERT_SQL = (
    "INSERT INTO houseinfo (title, house, address, struct, area, floor, maketime, price) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
)

with Path("data/houseinfo.csv").open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    records = [tuple(row[k] for k in FIELDS) for row in reader]

conn = pymysql.connect(**DB_CONFIG)
cur = None
try:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM houseinfo")
    before = cur.fetchone()[0]
    cur.execute("SELECT title, house, address, struct, area, floor, maketime, price FROM houseinfo")
    existed = {tuple(r) for r in cur.fetchall()}
    to_insert = [r for r in records if r not in existed]
    print(f"独立重跑：CSV {len(records)} 条，重跑前库内 {before} 条，待插入 {len(to_insert)} 条")
    if to_insert:
        cur.executemany(INSERT_SQL, to_insert)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM houseinfo")
    after = cur.fetchone()[0]
    print(f"重跑后条数 {after}，本次新增 {after - before}")
except Exception as exc:
    conn.rollback()
    print("已 rollback()，异常：", type(exc).__name__, exc)
    raise
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
    print("游标与连接已关闭")
