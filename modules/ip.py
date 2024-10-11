import json
import time
import os
import pandas as pd
from modules.neo4jconn import neo4j_db
from progress.bar import IncrementalBar

def ip(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    trust_input = args.trust_metter
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

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'ip_extended_bh_{time.strftime("%d_%m_%H_%M")}.txt'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    not_error = True
    if "json" in trust_input:
        bar = IncrementalBar('Done', max = len(data['assets']))
        count = 0
        with open(output_filename, "w") as f:
            for muz in data['assets'].values():
                ip = muz['ip_address']

                query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){muz["fqdn"]}.*" SET c.IP = {ip};\n'
                if args.neo4j_auth and not_error:
                        not_error = NJ.execute_query(query)
                    
                f.write(query)
                bar.next()

        print(f"\nDone: {count}")

    if "Assets" in trust_input:
        count = 0
        bar = IncrementalBar('Done', max = len(data))
        with open(output_filename, "w") as f:
            for index, row in data.iterrows():
                if pd.notna(row['IP Address']):
                    ip = row['IP Address'][1:-1].replace("'", "").split(', ')

                query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){row["FQDN"]}.*"  SET c.IP = {ip};\n'
                if args.neo4j_auth and not_error:
                    not_error = NJ.execute_query(query)
        
                f.write(query)
                bar.next()

    bar.finish()
    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")
        
    print(f"Out filename: {output_filename}")