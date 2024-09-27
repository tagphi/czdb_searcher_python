import sys
import time
from czdb.db_searcher import DbSearcher

if len(sys.argv) != 4:
    print(f"Usage: python {sys.argv[0]} <database_path> <query_type> <key>")
    sys.exit(1)

database_path = sys.argv[1]
query_type = sys.argv[2]
key = sys.argv[3]

db_searcher = DbSearcher(database_path, query_type, key)

while True:
    ip = input("Enter IP address (or type 'q' to quit): ")

    if ip.lower() == 'q':
        break

    start_time = time.time()

    try:
        region = db_searcher.search(ip)
        end_time = time.time()
        duration = end_time - start_time

        print("Search Results:")
        print(region)
        print(f"\nQuery Duration: {duration:.4f} seconds")
    except Exception as e:
        print(f"An error occurred during the search: {e}\nPlease try again.")

db_searcher.close()