import argparse
import sys
from modules.session import session
from modules.spray import spray
from modules.ntlm import ntlm
from modules.brute import brute
from modules.localadmin import localadmin
from modules.pre2k import pre2k

def arg_parse():
    parser = argparse.ArgumentParser(description='Application for upload data into BloodHound')
    subparser = parser.add_subparsers(title='subcommands', help='additional help')
    
    #__Start session part__
    session_parser = subparser.add_parser('session', help="Work with sessions")
    session_parser.add_argument('-si','--session_input', help="Session filename", required=True)
    session_parser.add_argument('-tm','--trust_metter', help="Trust metter json or csv filename", required=True)
    session_parser.add_argument('-o','--output', help="Output filename")

    session_parser.set_defaults(func=session)
    #__End session part__

    #__Start sprey part__
    spray_parser = subparser.add_parser('spray', help="Work with file from password spraying by cme ")
    spray_parser.add_argument('-i','--input', help="CME filename", required=True)
    spray_parser.add_argument('-o','--output', help="Output filename")
    spray_parser.add_argument('-nt','--nt_hash', help="If you password spraying by NT hash", action='store_true')    

    spray_parser.set_defaults(func=spray)
    #__End sprey part__
    
    #__Start ntlm part__
    ntlm_parser = subparser.add_parser('ntlm', help="Work with logs for search NTLMv2 hashes")
    ntlm_parser.add_argument('-i','--input', help="Log filenames", required=True, nargs="+")
    ntlm_parser.add_argument('-o','--output', help="Output filename")

    ntlm_parser.set_defaults(func=ntlm)
    #__End ntlm part__

    #__Start brute part__
    brute_parser = subparser.add_parser('brute', help="Find brutable service from Trust Metter report")
    brute_parser.add_argument('-tm','--trust_metter', help="Trust metter json or csv filename", required=True)
    brute_parser.add_argument('-o','--output', help="Output filename")
    brute_parser.add_argument('-p','--ports', help="Searching for ports. By default: 21, 22, 23, 1433, 3306, 5432, 5900", default=['21', '22', '23', '1433', '3306', '5432', '5900'], nargs='+')

    brute_parser.set_defaults(func=brute)
    #__End brute part__

    #__Start localadmin part__
    localadmin_parser = subparser.add_parser('localadmin', help="Add localadmin property from net rpc command"  )
    localadmin_parser.add_argument('-i','--input', help="Result net rpc command. Run script - script/localadmin.sh", required=True)
    localadmin_parser.add_argument('-tm','--trust_metter', help="Trust metter json or csv filename")
    localadmin_parser.add_argument('-o','--output', help="Output filename")
   
    localadmin_parser.set_defaults(func=localadmin)
    #__End brute part__

    #__Start pre2k part__
    pre2k_parser = subparser.add_parser('pre2k', help="Parse pre2k output")
    pre2k_parser.add_argument('-i','--input', help="pre2k output filename", required=True)
    pre2k_parser.add_argument('-o','--output', help="Output filename")
   
    pre2k_parser.set_defaults(func=pre2k)
    #__End pre2k part__

    #__Start neo4j part__
    modules = [session_parser, spray_parser, ntlm_parser, brute_parser, localadmin_parser , pre2k_parser]
    for module in modules:
        neo4j_goup = module.add_argument_group('neo4j')
        neo4j_goup.add_argument('-na', '--neo4j_auth', help="Auto use neo4j request for result", action='store_true' )
        neo4j_goup.add_argument('-nl', '--neo4j_login', help="Login for neo4j")
        neo4j_goup.add_argument('-np', '--neo4j_password', help="Password for neo4j")
        neo4j_goup.add_argument('-nu', '--neo4j_url', help='URL for neo4j. By default - neo4j://localhost:7687', default="neo4j://localhost:7687")
        neo4j_goup.add_argument('-nd', '--neo4j_database', help='Database for neo4j. By default - neo4j', default="neo4j")
    #__End neo4j part__

    args = parser.parse_args(sys.argv[1:])
    args.func(args)


def main():
    arg_parse()
    
if __name__ == "__main__":
    main()