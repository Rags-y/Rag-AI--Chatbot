from graph import driver


chunk_ids = [18, 29]


with driver.session() as session:

    result = session.run(
        """
        MATCH (c:Chunk)-[:MENTIONS]->(concept:Concept)
        WHERE c.id IN $chunk_ids

        RETURN
            c.id AS chunk_id,
            collect(concept.name) AS concepts

        ORDER BY c.id
        """,
        chunk_ids=chunk_ids,
    )

    for record in result:
        print(f"Chunk {record['chunk_id']}: {record['concepts']}")


driver.close()