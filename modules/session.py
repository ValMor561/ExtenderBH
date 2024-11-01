import re
import os
import json
import time
import pandas as pd
from modules.neo4jconn import neo4j_db

def session(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    session_input = args.session_input
    if args.trust_metter:
        trust_input = args.trust_metter
        if not ("json" in trust_input or "Assets" in trust_input):
            print("[!] Trust Metter must be json or *Assets.xlsx")
            return
        
        try:
            if "json" in trust_input:
                with open(trust_input, mode="r") as f:
                    tm_data = json.load(f)
            elif "Assets" in trust_input:
                tm_data = pd.read_excel(trust_input)
        except FileNotFoundError:
            print("[!] Check the trust metter filename")
            return   
    else:
        trust_input = ""

    try:
        with open(session_input, mode="r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("[!] Check the session filename")
        return

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'session_extended_bh_{time.strftime("%d_%m_%H_%M")}.cypher'

    
    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    not_error = True
    count = 0
    for line in data:
        match = re.search(r"\[\*\]\s([^:\s]*):?\s\[([^]^\*]*)\]", line)
        if match:
            target = match[1]
            matches = re.findall(r"\[([^]^\*]*)\]", line)
            if matches:
                for uz in matches:
                    use_ip = False
                    match = re.search(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", target)
                    if match:
                        if "json" in trust_input:
                            for muz in tm_data['assets'].values():
                                if target in muz['ip_address']:
                                    target = muz['fqdn']
                                    break
                        elif "xlsx" in trust_input:
                            for index, row in tm_data.iterrows():
                                ip_addr = row['IP Address'][2:-2].replace('\'', '').split(', ')
                                if target in ip_addr:
                                    target = row['FQDN']
                                    break
                        else:
                            query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE "{target}" in m.IP MERGE (m)-[r:HasSession]->(n);\n'
                            use_ip = True
                    if not use_ip:
                        query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE m.name ~= "(?i){target}.*" MERGE (m)-[r:HasSession]->(n);\n'
                    
                    if args.neo4j_auth and not_error:
                        not_error = NJ.execute_query(query)
                    
                    with open(output_filename, "a") as f:
                        f.write(query)
                    print(f'[+] {target} -> {uz}')
                    count += 1
                    
    print(f"Added {count} sessions")
    print(f"Out filename: {output_filename}")
