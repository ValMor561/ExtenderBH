from modules.neo4jconn import neo4j_db
import re
import json
import pandas as pd
import time
import os

def localadmin(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    not_error = True
    input = args.input
    trust_input = ""
    if args.trust_meter:
        trust_input = args.trust_meter
        if not ("json" in trust_input or "Assets" in trust_input):
            print("[!] Trust meter must be json or *Assets.xlsx")
            return
        
    try:
        with open(input, mode="r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("[!] Check the input filename")
        return
    
    if args.output:
        output_filename = args.output
    else:
        output_filename = f'localadmin_extended_bh_{time.strftime("%d_%m_%H_%M")}.cypher'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension
    
    localadmin_dict = {}
    for line in data:
        match = re.search(r"\[\+\]\s(.*)", line)
        if match:
            target = match[1]
            localadmin_dict[target] = []
        else:
            if line == "\n":
                continue
            localadmin_dict[target].append(line.strip())
    
    if trust_input != "":
        try:
            if "json" in trust_input:
                with open(trust_input, mode="r") as f:
                    data = json.load(f)
            elif "Assets" in trust_input:
                data = pd.read_excel(trust_input)
        except FileNotFoundError:
            print("[!] Check the trust meter filename")
            return
    count = 0
    for target in localadmin_dict:      
        match = re.search(r"([0-9]{1,3}[\.]){3}[0-9]{1,3}", target)
        if match:
            if trust_input != "":
                if "json" in trust_input:
                    for muz in data['assets'].values():
                        if target in muz['ip_address']:
                            target_fqdn = muz['fqdn']
                elif "Assets" in trust_input:
                    for index, row in data.iterrows():
                        ip_addr = row['IP Address'][2:-2].replace('\'', '').split(', ')
                        if target in ip_addr:
                            target_fqdn = row['FQDN']
        for admin in localadmin_dict[target]:
            try:
                domain, username = admin.split("\\")
            except:
                continue
            query = f'MATCH (u) WHERE u.name =~ "(?i){username}@{domain}.*" MATCH (c: Computer) WHERE c.name =~ "(?i){target_fqdn}.*" MERGE (u)-[r: AdminTo]->(c) SET u.LocalAdmin = True;\n'
            if args.neo4j_auth and not_error:
                not_error = NJ.execute_query(query)
                    
            with open(output_filename, "a") as f:
                f.write(query)
            count += 1
    
    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")

    print(f"Found: {count} users")
    print(f"Out filename: {output_filename}")