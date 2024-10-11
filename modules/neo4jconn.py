import neo4j
from neo4j.exceptions import DriverError, Neo4jError, AuthError

class neo4j_db:
    def __init__(self, url, user, passw, database):
        self.driver = neo4j.GraphDatabase.driver(url, auth=(user, passw), encrypted=False)
        self.database = database
    def close(self):
        self.driver.close()

    def execute_query(self, query):
        try:
            self.driver.execute_query(query, database_=self.database)
            return True
        except AuthError:
            print("[!] Chech neo4j auth data\n")
            return False
        except (DriverError, Neo4jError) as exception:
            print("[!]" + exception)
            return False
        except Exception as exception:
            print("[!]" + exception)
            return False
            
