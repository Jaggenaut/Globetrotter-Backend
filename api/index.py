from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import random

from api.database import get_db
from api.models import PlaceData, User

app = FastAPI()

# Allow all origins for testing, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Get Random Place Question
@app.get("/places/random")
def get_random_place():
    db = next(get_db())  # Manually get the database session

    try:
        place = db.query(PlaceData).order_by(func.random()).first()
        if not place:
            return JSONResponse(content={"error": "No places found."}, status_code=404)

        clues = random.sample(place.clues, min(2, len(place.clues)))

        return JSONResponse(content={
            "question_id": place.id,
            "clues": clues,
            "options": get_random_options(db, place.city),
        })
    finally:
        db.close()


def get_random_options(db: Session, correct_city: str):
    all_places = db.query(PlaceData.city).all()
    all_cities = [p.city for p in all_places if p.city != correct_city]
    options = random.sample(all_cities, 3) + [correct_city]
    random.shuffle(options)
    return options


# ✅ Check Answer
@app.post("/places/guess")
def check_answer(question_id: int, user_answer: str):
    db = next(get_db())

    try:
        place = db.query(PlaceData).filter(PlaceData.id == question_id).first()
        if not place:
            return JSONResponse(content={"error": "Question not found."}, status_code=404)

        correct = place.city.lower() == user_answer.lower()

        return JSONResponse(content={
            "correct": correct,
            "fun_fact": random.choice(place.fun_fact)
        })
    finally:
        db.close()


# ✅ Update Score
@app.post("/users/score")
def update_score(user_id: int, correct: bool):
    db = next(get_db())

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(content={"error": "User not found."}, status_code=404)

        if correct:
            user.correct_answers += 1
        else:
            user.incorrect_answers += 1

        db.commit()
        return JSONResponse(content={"message": "Score updated successfully!"})
    finally:
        db.close()


# ✅ Retrieve User Score
@app.get("/users/score/{user_id}")
def get_score(user_id: int):
    db = next(get_db())

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(content={"error": "User not found."}, status_code=404)

        score = user.correct_answers * 10 - user.incorrect_answers * 2

        return JSONResponse(content={"score": score, "message": "Score fetched successfully"})
    finally:
        db.close()


# ✅ Register User
@app.post("/users/register")
def register_user(username: str):
    db = next(get_db())

    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return JSONResponse(content={"message": "Username already taken", "user_id": existing_user.id})

        new_user = User(username=username)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return JSONResponse(content={"message": "User registered successfully!", "user_id": new_user.id})
    finally:
        db.close()
