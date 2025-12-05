# backend/app.py
from flask import Flask, jsonify, request, abort
from dotenv import load_dotenv
import os

load_dotenv()

from database import SessionLocal
from models import Question, Answer, init_db
from neo4j_client import save_question_tags, get_related_by_tags

app = Flask(__name__)

# ensure DB tables exist
init_db()

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/questions", methods=["GET"])
def list_questions():
    db = SessionLocal()
    qs = db.query(Question).order_by(Question.created_at.desc()).all()
    result = [{"id": q.id, "title": q.title, "body": q.body, "tags": q.tags, "created_at": q.created_at.isoformat()} for q in qs]
    db.close()
    return jsonify(result)

@app.route("/questions", methods=["POST"])
def create_question():
    payload = request.get_json()
    if not payload or "title" not in payload or "body" not in payload:
        abort(400, "title and body are required")
    db = SessionLocal()
    q = Question(title=payload["title"], body=payload["body"], tags=payload.get("tags"))
    db.add(q)
    db.commit()
    db.refresh(q)
    # sync to neo4j
    try:
        save_question_tags(q.id, q.title, q.tags)
    except Exception as e:
        app.logger.error("Neo4j sync failed: %s", e)
    db.close()
    return jsonify({"id": q.id, "message": "created"}), 201

@app.route("/questions/<int:qid>", methods=["GET"])
def get_question(qid):
    db = SessionLocal()
    q = db.query(Question).get(qid)
    if not q:
        abort(404)
    answers = [{"id": a.id, "body": a.body, "created_at": a.created_at.isoformat()} for a in q.answers]
    related = []
    try:
        related = get_related_by_tags(qid)
    except Exception as e:
        app.logger.debug("Neo4j related failed: %s", e)
    db.close()
    return jsonify({
        "id": q.id,
        "title": q.title,
        "body": q.body,
        "tags": q.tags,
        "answers": answers,
        "related": related
    })

@app.route("/questions/<int:qid>/answers", methods=["POST"])
def add_answer(qid):
    payload = request.get_json()
    if not payload or "body" not in payload:
        abort(400, "body is required")
    db = SessionLocal()
    q = db.query(Question).get(qid)
    if not q:
        abort(404, "question not found")
    a = Answer(question_id=qid, body=payload["body"])
    db.add(a)
    db.commit()
    db.refresh(a)
    db.close()
    return jsonify({"id": a.id, "message": "answer added"}), 201

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
