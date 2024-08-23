import json
import time
import os
from modules.neo4jconn import neo4j_db

def brute(args):
    if args.neo4j_auth:
        if not args.neo4j_login:
            print("[!] neo4j auth mode required --neo4j_login or -nl flag")
            return
        if not args.neo4j_password:
            print("[!] neo4j auth mode required --neo4j_password or -np flag")
            return
        NJ = neo4j_db(args.neo4j_url, args.neo4j_login, args.neo4j_password, args.neo4j_database)

    trust_input = args.trust_metter
    if "json" not in trust_input:
        print("[!] Trust Metter must be json")
        return
    
    try:
        with open(trust_input, mode="r") as f:
            data = json.load(f) 
    except FileNotFoundError:
        print("[!] Check the trust metter filename")
        return

    if args.output:
        output_filename = args.output
    else:
        output_filename = f'extended_brute_bh_{time.strftime("%d_%m_%H_%M")}.txt'

    if os.path.exists(output_filename):
        filename, file_extension = os.path.splitext(output_filename)
        output_filename = filename + "_tmp" + file_extension

    search_port = args.ports
    not_error = True
    count = 0
    print(f'{"-"*20}Start{"-"*20}\n')
    for muz in data['assets'].values():
        if muz['wave'] == 'Inaccessible':
            continue
        open_port = muz['tcp_ports']
        if muz['udp_ports'] != "":
            open_port += ", " + muz['udp_ports']
        open_port = open_port.split(', ')

        found_port = list(set(open_port) & set(search_port))
        if len(found_port) == 0:
            continue

        found_port_str = ', '.join(found_port)
        print(f"[+] For {muz['fqdn']} found {len(found_port)} brutable service on {found_port_str}")
        query = f'MATCH (c:Computer) WHERE c.name =~ "(?i){muz["fqdn"]}.*" SET c.BrutableService = {found_port};\n'

        if args.neo4j_auth and not_error:
                not_error = NJ.execute_query(query)
            
        with open(output_filename, "a+") as f:
            f.write(query)
        count += 1

    print(f"\nDone: {count}")

    if args.neo4j_auth:
        if not_error:
            print("Data upload in neo4j succesfully")
        else:
            print("Couldn't upload data, you can do it manualy")
        
    print(f"Out filename: {output_filename}")