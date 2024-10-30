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
        resolve_bh = False
    else:
        resolve_bh = True
    
    
    try:
        with open(session_input, mode="r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("[!] Check the session filename")
        return

    ses_uz = {}
    for line in data:
        match = re.search(r"\[\*\]\s([^:\s]*)", line)
        if match:
            target = match[1]
            matches = re.findall(r"\[([^]^\*]*)\]", line)
            if matches:
                for match in matches:
                    if match not in ses_uz.keys(): 
                        ses_uz[match] = [target]
                    else:
                        ses_uz[match].append(target)

    if len(ses_uz) == 0:
        print("[!] Make sure that your session file has format <ip> : [UZ]")
    
    
    

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'session_extended_bh_{time.strftime("%d_%m_%H_%M")}.cypher'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    not_error = True
    count = 0
    if not resolve_bh:
        if not ("json" in trust_input or "Assets" in trust_input):
            print("[!] Trust Metter must be json or *Assets.xlsx")
            return
        try:
            if "json" in trust_input:
                with open(trust_input, mode="r") as f:
                    data = json.load(f)
            elif "Assets" in trust_input:
                data = pd.read_excel(trust_input)
        except FileNotFoundError:
            print("[!] Check the trust metter filename")
            return 
        if "json" in trust_input:
            for uz, targets in ses_uz.items():
                for target in targets:
                    muz_n = ""
                    match = re.search(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", target)
                    if match:
                        for muz in data['assets'].values():
                            if target in muz['ip_address']:
                                muz_n = muz['fqdn']
                                break
                    else:
                        muz_n = target
                    if muz_n == "":
                        continue     
                    query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE m.name =~ "(?i){muz_n}.*" MERGE (n)-[r:HasSession]->(m);\n'
                    
                    if args.neo4j_auth and not_error:
                        not_error = NJ.execute_query(query)
                    
                    with open(output_filename, "a") as f:
                        f.write(query)
                    print(f'[+] {muz_n} -> {uz}')
                    count += 1

        elif "Assets" in trust_input:
            for uz, targets in ses_uz.items():
                for target in targets:
                    muz_n = ""
                    match = re.search(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", target)
                    if match:
                        for index, row in data.iterrows():
                            ip_addr = row['IP Address'][2:-2].replace('\'', '').split(', ')
                            if target in ip_addr:
                                muz_n = row['FQDN']
                                break
                    else:
                        muz_n = target
                    if muz_n == "":
                        continue
                    query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE m.name =~ "(?i){muz_n}.*" MERGE (m)-[r:HasSession]->(n);\n'
                    
                    if args.neo4j_auth and not_error:
                        not_error = NJ.execute_query(query)
                    
                    with open(output_filename, "a") as f:
                        f.write(query)
                    print(f'[+] {muz_n} -> {uz}')
                    count += 1
                    
    else:
        for uz, targets in ses_uz.items():
            for target in targets:
                match = re.search(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", target)
                if match:
                    query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE "{target}" in m.IP MERGE (m)-[r:HasSession]->(n);\n'
                else:
                    query = f'MATCH (n:User) WHERE n.name =~ "(?i){uz}.*" MATCH (m:Computer) WHERE m.name ~= "(?i){target}.*" MERGE (m)-[r:HasSession]->(n);\n'

                if args.neo4j_auth and not_error:
                    not_error = NJ.execute_query(query)
                
                with open(output_filename, "a") as f:
                    f.write(query)
                print(f'[+] {target} -> {uz}')
    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")
    print(f"Added {count} sessions")
    print(f"Out filename: {output_filename}")
