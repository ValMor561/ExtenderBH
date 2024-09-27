import re
import time
import os
from modules.neo4jconn import neo4j_db

def ntlm(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'extended_ntlm_bh_{time.strftime("%d_%m_%H_%M")}.txt'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    user_list = {}
    responder_logs = args.input
    not_error = True
    print(f'{"-"*20}Start{"-"*20}\n')
    for file in responder_logs:
        try:
            with open(file, mode="r") as f:
                data = f.readlines()
        except FileNotFoundError:
            print(f"[!] Check {file} filename")
            return
        
        for line in data:
            match = re.search(r"(.*)::[^:]*:[^:]{16}:[^:]{32}:.*", line)
            if match:
                user = match[1]
                if user not in user_list:
                    user_list[user] = 1
                else:
                    user_list[user] += 1
    
    count = 0
    for user, freq in user_list.items():
        print(f"[+] User {user} encountered {freq} time")
        query = f'MATCH (n) WHERE n.samaccountname =~ "(?i){user}" SET n.NTLMv2_Count = {freq};\n'
        if args.neo4j_auth and not_error:
            not_error = NJ.execute_query(query)
            
        with open(output_filename, "a") as f:
            f.write(query)
        count += 1
    
    print(f"\nFound: {count} users")

    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")
        
    print(f"Out filename: {output_filename}")