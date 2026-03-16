# sqldump
SQLite database dumper: export tables to JSON, CSV, SQL, or Markdown.
```bash
python sqldump.py mydb.sqlite --tables
python sqldump.py mydb.sqlite users -f csv
python sqldump.py mydb.sqlite -f json -o exports/
python sqldump.py mydb.sqlite orders -w "status='shipped'" -l 100
```
## Zero dependencies. Python 3.6+.
