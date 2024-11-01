from modules.neo4jconn import neo4j_db
import time
import os
import re

def pre2k(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    pre2k_input = args.input
    try:
        with open(pre2k_input, mode="r") as f:
            data = f.readlines()
    except FileNotFoundError:
        print("[!] Check the input filename")
        return
    
    if args.output:
        output_filename = args.output
    else:
        output_filename = f'pre2k_extended_bh_{time.strftime("%d_%m_%H_%M")}.cypher'

    if os.path.exists(output_filename):
            filename, file_extension = os.path.splitext(output_filename)
            output_filename = filename + "_tmp" + file_extension

    found = {}
    not_error = True
    count = 0
    for line in data:
        match = re.search(r"VALID CREDENTIALS:\s([^\\]*)\\([^:]*):(\S*)", line)
        if match:
            domain = match[1]
            user = match[2]
            password = match[3]

            if password == "nopass":
                password = ""

            if user in found.keys():
                continue
            found[user] = password
            
            print(f"[+] Valid: {user}:{password}")
            query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){user[:-1]}.{domain}.*" SET c.ClearTextPassword = "{password}" SET c.owned = True;\n'
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
    print(f"Found {count} valid cred")
    print(f"Out filename: {output_filename}")