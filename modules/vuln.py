import re
import time
import os
from modules.neo4jconn import neo4j_db
from progress.bar import IncrementalBar

def vuln(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    cme_input = args.input
    try:
        with open(cme_input, mode="r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("[!] Check the input filename")
        return

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'vuln_extended_bh_{time.strftime("%d_%m_%H_%M")}.cypher'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    not_error = True
    count = 0
    bar = IncrementalBar('Done', max=len(data))
    for line in data:
        match_plus = re.search(r"445\s*(\S*)\s*(WebClient)?(Vulnerable, next step https:\/\/github.com\/ly4k\/PrintNightmare)?", line)
        if match_plus:
            target = match_plus[1]
            if match_plus[2]:
                query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){target}.*" SET c.owned = True, c.Vuln = CASE WHEN c.Vuln IS NULL THEN ["WebDav"] WHEN NOT "WebDav" IN c.Vuln THEN c.Vuln + "WebDav" ELSE c.Vuln END;\n'
            elif match_plus[3]:
                query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){target}.*" SET c.owned = True, c.Vuln = CASE WHEN c.Vuln IS NULL THEN ["PrintNightmare"] WHEN NOT "PrintNightmare" IN c.Vuln THEN c.Vuln + "PrintNightmare" ELSE c.Vuln END;\n'
            if args.neo4j_auth and not_error:
                not_error = NJ.execute_query(query)
            
            with open(output_filename, "a") as f:
                f.write(query)
                bar.next()
            count += 1

    if args.neo4j_auth:
        if not_error:
            print("\nData upload in neo4j succesfully")
        else:
            print("\nCouldn't upload data, you can do it manualy")
        
    print(f"\nOut filename: {output_filename}")