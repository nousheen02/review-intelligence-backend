from fastapi import FastAPI, UploadFile, File, Depends
import pandas as pd
from sqlalchemy.orm import Session
from io import StringIO
from database import SessionLocal, engine
from models import Base, Review
from sentiment import classify_sentiment
from keyword_extract import extract_keywords
from wordcloud_gen import generate_wordcloud
from insights import get_insights

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))
    df["sentiment"] = df["review"].apply(classify_sentiment)
    for _, row in df.iterrows():
        db.add(Review(text=row["review"], sentiment=row["sentiment"]))
    db.commit()
    generate_wordcloud(df["review"].tolist())
    return {"status": "uploaded", "summary": df["sentiment"].value_counts().to_dict()}

@app.get("/summary")
def summary(db: Session = Depends(get_db)):
    reviews = db.query(Review).all()
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}
    for r in reviews:
        sentiments[r.sentiment] += 1
    return sentiments

@app.get("/keywords")
def keywords(db: Session = Depends(get_db)):
    reviews = [r.text for r in db.query(Review).all()]
    return {"keywords": extract_keywords(" ".join(reviews))}

@app.get("/samples")
def samples(db: Session = Depends(get_db)):
    return {
        "positive": [r.text for r in db.query(Review).filter(Review.sentiment == "Positive").limit(3)],
        "negative": [r.text for r in db.query(Review).filter(Review.sentiment == "Negative").limit(3)],
    }

@app.get("/insights")
def insights(db: Session = Depends(get_db)):
    reviews = pd.DataFrame([(r.text, r.sentiment) for r in db.query(Review)], columns=["review", "sentiment"])
    return {"insights": get_insights(reviews)}
@app.get("/")
def read_root():
    return {"message": "Backend API is running! Visit /docs for Swagger UI."}

