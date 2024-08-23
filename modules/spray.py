import re
import time
import os
from modules.neo4jconn import neo4j_db

def spray(args):
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
        output_filename = f'extended_spray_bh_{time.strftime("%d_%m_%H_%M")}.txt'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    user_res = []
    passw_res = []
    user_change = []
    not_error = True
    count = 0
    print(f'{"-"*20}Start{"-"*20}\n')
    for line in data:
        match_plus = re.search(r"([^\s]*)\s*\[\+\]\s([^\\]*)\\([^:]*):([^\s]*)\s?(\(Zh@hnut\))?(Pwn3d!)?", line)
        if match_plus:
            target = match_plus[1]
            domain = match_plus[2]
            user = match_plus[3]
            passw = match_plus[4]
            zhahnut = match_plus[5]
            pwned = match_plus[6]
            localadmin = ""

            if user in user_res:
                continue
            user_res.append(user)

            if zhahnut or pwned:
                localadmin = "SET u.LocalAdmin = True"
                print(f"[+] Valid localadmin: {user}:{passw}")
                if target:
                    query = f'MATCH (u:User) WHERE u.name =~ "(?i){user}.*" MATCH (c: Computer) WHERE c.name =~ "(?i){target}.*" MERGE (u)-[r: AdminTo]->(c);\n'
                    if args.neo4j_auth and not_error:
                        not_error = NJ.execute_query(query)
                    
                    with open(output_filename, "a+") as f:
                        f.write(query)
            else:
                print(f"[+] Valid user: {user}:{passw}")

            if args.nt_hash:
                query = f'MATCH (u:User) WHERE u.name =~ "(?i){user}.*" SET u.owned = True {localadmin};\n'
            else:
                query = f'MATCH (u:User) WHERE u.name =~ "(?i){user}.*" SET u.ClearTextPassword = "{passw}" SET u.owned = True {localadmin};\n'
                if passw not in passw_res:
                    passw_res.append(passw)
            
            if args.neo4j_auth and not_error:
                not_error = NJ.execute_query(query)
            
            with open(output_filename, "a+") as f:
                f.write(query)
            count += 1

        if args.nt_hash:
            continue

        match_change = re.search(r"\[\-\]\s([^\\]*)\\([^:]*):([^\s]*)\sSTATUS_PASSWORD_MUST_CHANGE", line)
        if match_change:
            domain = match_change[1]
            user = match_change[2]
            passw = match_change[3]

            if user in user_change:
                continue
            user_change.append(user)
            
            query = f'MATCH (u:User) WHERE u.name =~ "(?i){user}.*" SET u.PasswordMustBeChange = True SET u.OldPassword = "{passw}" SET u.owned = True;\n'

            print(f"[+] Password {passw} must be change for user {user}")

            if args.neo4j_auth and not_error:
                not_error = NJ.execute_query(query)

            with open(output_filename, "a+") as f:
                f.write(query)
            count += 1
        


    for passw in passw_res:
        query = f'MATCH (n:User) WHERE n.ClearTextPassword = "{passw}" MATCH (m:User) WHERE m.ClearTextPassword = "{passw}" FOREACH (_ IN CASE WHEN n <> m THEN [1] END | MERGE (n)-[r:SharePasswordWith]->(m));\n'
        if args.neo4j_auth and not_error:
            not_error = NJ.execute_query(query)
            
        with open(output_filename, "a+") as f:
            f.write(query)

    print(f"\nFound: {count} users")

    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")
        
    print(f"Out filename: {output_filename}")