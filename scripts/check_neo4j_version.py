from neo4j import GraphDatabase

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
    ),
)


try:

    driver.verify_connectivity()

    print("Neo4j connection successful!\n")

    with driver.session() as session:

        result = session.run(
            """
            CALL dbms.components()
            YIELD name, versions, edition
            RETURN name, versions, edition
            """
        )

        for record in result:

            print("Name:")
            print(record["name"])

            print("\nVersion:")
            print(record["versions"])

            print("\nEdition:")
            print(record["edition"])

except Exception as e:

    print("Error:")
    print(e)

finally:

    driver.close()