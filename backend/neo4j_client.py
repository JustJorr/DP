# backend/neo4j_client.py
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "test")

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def save_question_tags(qid, title, tags):
    """Create Question node and HAS_TAG relationships. tags: comma separated string"""
    driver = get_driver()
    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
    with driver.session() as session:
        session.run("MERGE (q:Question {id: $id}) SET q.title = $title", id=str(qid), title=title)
        for t in tag_list:
            session.run("""
            MERGE (tag:Tag {name: $tag})
            MATCH (q:Question {id: $id})
            MERGE (q)-[:HAS_TAG]->(tag)
            """, tag=t, id=str(qid))

def get_related_by_tags(qid, limit=5):
    """Return related question ids with number of shared tags"""
    driver = get_driver()
    q = driver.session().run("""
    MATCH (q:Question {id:$id})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(other:Question)
    WHERE other.id <> $id
    RETURN other.id AS id, other.title AS title, count(t) AS commonTags
    ORDER BY commonTags DESC
    LIMIT $limit
    """, id=str(qid), limit=limit)
    return [record.data() for record in q]
