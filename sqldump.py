#!/usr/bin/env python3
"""sqldump - SQLite database dumper and format converter."""
import sqlite3, argparse, json, csv, sys, os

def main():
    p = argparse.ArgumentParser(description='SQLite database dumper')
    p.add_argument('db', help='Database file')
    p.add_argument('table', nargs='?', help='Table name (all if omitted)')
    p.add_argument('-f', '--format', choices=['json','csv','sql','markdown'], default='json')
    p.add_argument('-o', '--output', help='Output directory for multi-table')
    p.add_argument('-w', '--where', help='WHERE clause')
    p.add_argument('-l', '--limit', type=int)
    p.add_argument('--tables', action='store_true', help='List tables only')
    args = p.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    if args.tables:
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            count = conn.execute(f"SELECT COUNT(*) FROM [{row[0]}]").fetchone()[0]
            print(f"  {row[0]:<30} {count:>8} rows")
        return

    tables = [args.table] if args.table else [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]

    for table in tables:
        query = f"SELECT * FROM [{table}]"
        if args.where: query += f" WHERE {args.where}"
        if args.limit: query += f" LIMIT {args.limit}"
        
        rows = conn.execute(query).fetchall()
        if not rows: continue
        cols = rows[0].keys()

        if args.output and len(tables) > 1:
            os.makedirs(args.output, exist_ok=True)
            ext = {'json': 'json', 'csv': 'csv', 'sql': 'sql', 'markdown': 'md'}[args.format]
            outfile = open(os.path.join(args.output, f"{table}.{ext}"), 'w')
        else:
            outfile = sys.stdout

        if args.format == 'json':
            outfile.write(json.dumps([dict(r) for r in rows], indent=2, default=str))
            outfile.write('\n')
        elif args.format == 'csv':
            w = csv.writer(outfile)
            w.writerow(cols)
            for r in rows: w.writerow(list(r))
        elif args.format == 'sql':
            for r in rows:
                vals = ', '.join(repr(v) if v is not None else 'NULL' for v in r)
                outfile.write(f"INSERT INTO [{table}] VALUES ({vals});\n")
        elif args.format == 'markdown':
            outfile.write(f"# {table}\n\n")
            outfile.write('| ' + ' | '.join(cols) + ' |\n')
            outfile.write('|' + '|'.join('---' for _ in cols) + '|\n')
            for r in rows:
                outfile.write('| ' + ' | '.join(str(v)[:30] for v in r) + ' |\n')

        if outfile != sys.stdout:
            outfile.close()
            print(f"  Exported {table}: {len(rows)} rows")

if __name__ == '__main__':
    main()
