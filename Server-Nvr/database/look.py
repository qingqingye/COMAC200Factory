import mylib
import sqlite3 as sql
conn = sql.connect('info.db')
mylib.pt_table(conn,'gate_table')
mylib.pt_table(conn,'heatmap_table')
