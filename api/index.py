from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
import random

from api.database import get_db
from api.models import PlaceData, User

app = FastAPI()

# ✅ Allow CORS (Update in Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request Body Models
class UserRegisterRequest(BaseModel):
    username: str

class GuessRequest(BaseModel):
    question_id: int
    user_answer: str

class ScoreUpdateRequest(BaseModel):
    user_id: int
    correct: bool


# ✅ Get Random Place Question
@app.get("/places/random")
def get_random_place(db: Session = Depends(get_db)):
    place = db.query(PlaceData).order_by(func.random()).first()
    if not place:
        raise HTTPException(status_code=404, detail="No places found.")

    clues = random.sample(place.clues, min(2, len(place.clues)))  # Get 1-2 clues

    return {
        "question_id": place.id,
        "clues": clues,
        "options": get_random_options(db, place.city),
    }

def get_random_options(db: Session, correct_city: str):
    all_places = db.query(PlaceData.city).all()
    all_cities = [p.city for p in all_places if p.city != correct_city]
    options = random.sample(all_cities, 3) + [correct_city]  # 3 wrong + 1 correct
    random.shuffle(options)
    return options


# ✅ Check Answer API
@app.post("/places/guess")
def check_answer(data: GuessRequest, db: Session = Depends(get_db)):
    place = db.query(PlaceData).filter(PlaceData.id == data.question_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Question not found.")

    correct = place.city.lower() == data.user_answer.lower()

    return {
        "correct": correct,
        "correct_ans": place.city,
        "fun_fact": random.choice(place.fun_fact)
    }


# ✅ Update User Score
@app.post("/users/score")
def update_score(data: ScoreUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if data.correct:
        user.correct_answers += 1
    else:
        user.incorrect_answers += 1

    db.commit()
    return {"message": "Score updated successfully!"}


# ✅ Get User Score
@app.get("/users/score/{user_id}")
def get_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "score": (user.correct_answers * 10 - user.incorrect_answers * 2),
        "message": "Score fetched successfully"
    }


# ✅ Register User API
@app.post("/users/register")
def register_user(data: UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == data.username).first()
    if existing_user:
        return {"message": "Username already taken", "user_id": existing_user.id}

    new_user = User(username=data.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully!", "user_id": new_user.id}
