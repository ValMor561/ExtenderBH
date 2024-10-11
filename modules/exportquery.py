from modules.neo4jconn import neo4j_db
from progress.bar import IncrementalBar

def exportquery(args):
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
    
    bar = IncrementalBar('Done', max = len(data))
    for line in data:
        not_error = NJ.execute_query(line)
        if not not_error:
            return
        bar.next()
    print("Done!")