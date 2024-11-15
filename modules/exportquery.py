import concurrent.futures
from modules.neo4jconn import neo4j_db
from progress.bar import IncrementalBar
import threading
import time

def execute_query_in_thread(query, NJ, bar, lock):
    not_error = NJ.execute_query(query)
    
    with lock:
        bar.next()
    
    return not_error

def exportquery(args):
    start = time.time()
    threads = int(args.threads)

    if not args.neo4j_login:
        print("[!] neo4j auth mode required --neo4j_login or -nl flag")
        return
    if not args.neo4j_password:
        print("[!] neo4j auth mode required --neo4j_password or -np flag")
        return
    
    NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)
    
    query_list = args.input
    with open(query_list, mode="r") as f:
        data = f.readlines()
    
    bar = IncrementalBar('Done', max=len(data))
    
    lock = threading.Lock()
    
    not_error = True
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        
        for line in data:
            futures.append(executor.submit(execute_query_in_thread, line, NJ, bar, lock))
        
        for future in concurrent.futures.as_completed(futures):
            if not future.result():  
                not_error = False
                break
    
    if not not_error:
        print("\nAn error occurred during query execution.")
