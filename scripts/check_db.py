import sqlite3

conn = sqlite3.connect('data/crisislens.db')
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# If events table exists, check one event
if any(t[0] == 'crisis_events' for t in tables):
    cursor.execute('SELECT post_id, severity, reasoning, recommended_action FROM crisis_events LIMIT 1')
    row = cursor.fetchone()
    if row:
        print("\nFirst event:")
        print(f"  post_id: {row[0]}")
        print(f"  severity: {row[1]}")
        print(f"  reasoning: {row[2][:80] if row[2] else 'NULL'}")
        print(f"  action: {row[3][:80] if row[3] else 'NULL'}")
    else:
        print("\nNo events in table")
elif any(t[0] == 'events' for t in tables):
    cursor.execute('SELECT post_id, severity, reasoning, recommended_action FROM events LIMIT 1')
    row = cursor.fetchone()
    if row:
        print("\nFirst event:")
        print(f"  post_id: {row[0]}")
        print(f"  severity: {row[1]}")
        print(f"  reasoning: {row[2][:80] if row[2] else 'NULL'}")
        print(f"  action: {row[3][:80] if row[3] else 'NULL'}")
    else:
        print("\nNo events in table")
conn.close()
