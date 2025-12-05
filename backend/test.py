from neo4j import GraphDatabase

driver = GraphDatabase.driver("Bolt://localhost:7687", auth=("neo4j", "user1234"))
session = driver.session()
print(session.run("Return Kontol AS test ").single())