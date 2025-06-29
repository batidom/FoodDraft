from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware 
from restaurant_api.models import Restaurant
from restaurant_api.database import SessionLocal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/restaurants")
def read_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@app.get("/header_image/{restaurant_id}")
def get_header_image(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if restaurant:
        return {"header_image": restaurant.header_image}
    return {"error": "Restaurant not found"}