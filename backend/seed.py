# backend/seed.py
from database import SessionLocal
from models import Question, Answer, init_db
from neo4j_client import save_question_tags

def seed():
    init_db()
    db = SessionLocal()
    q1 = Question(title="How to install Flask?", body="I can't install Flask on Windows.", tags="python,flask")
    q2 = Question(title="Neo4j relationships best practice", body="How to design tags in Neo4j?", tags="neo4j,graph")
    db.add_all([q1, q2])
    db.commit()
    # sync
    for q in db.query(Question).all():
        save_question_tags(q.id, q.title, q.tags)
    db.close()
    print("Seeded demo data.")

if __name__ == "__main__":
    seed()
