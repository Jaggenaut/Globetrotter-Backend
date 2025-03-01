from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api.database import get_db
from api.models import PlaceData, User
from sqlalchemy.sql import func
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()


# Allow requests from all origins (not recommended for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Get Question from this API
@app.get("/places/random")
def get_random_place(db: Session = Depends(get_db)):
    place = db.query(PlaceData).order_by(func.random()).first()
    if not place:
        return {"error": "No places found."}
    
    clues = random.sample(place.clues, min(2, len(place.clues)))  # Get 1-2 clues

    return {
        "question_id": place.id,  # Needed for answer verification
        "clues": clues,
        "options": get_random_options(db, place.city),  # Multiple-choice options
    }

def get_random_options(db: Session, correct_city: str):
    all_places = db.query(PlaceData.city).all()
    all_cities = [p.city for p in all_places if p.city != correct_city]
    options = random.sample(all_cities, 3) + [correct_city]  # 3 wrong + 1 correct
    random.shuffle(options)
    return options



# Check the answer and return Fun Facts
@app.post("/places/guess")
def check_answer(question_id: int, user_answer: str, db: Session = Depends(get_db)):
    place = db.query(PlaceData).filter(PlaceData.id == question_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Question not found.")
    
    correct = place.city.lower() == user_answer.lower()
    
    return {
        "correct": correct,
        "fun_fact": random.choice(place.fun_fact)  # Show random fun fact
    }


# Score of the the User
@app.post("/users/score")
def update_score(user_id: int, correct: bool, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if correct:
        user.correct_answers += 1
    else:
        user.incorrect_answers += 1

    db.commit()
    return {"message": "Score updated successfully!"}


# Score retrieval
@app.get("/users/score/{user_id}")
def get_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"score":(user.correct_answers*10 - user.incorrect_answers*2),
            "message": "Score fetched sucessfully"}


# Register User
@app.post("/users/register")
def register_user(username: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return {"message": "Username already taken", "user_id": existing_user.id}

    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully!", "user_id": new_user.id}