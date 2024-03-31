from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.fastapi_userauth
collection = db.users

class User(BaseModel):
    username: str
    email: str
    password: str

app = FastAPI()

@app.post("/api/v1/user/create")
def home_page(user:User):
    existing_user = collection.find_one({"email":user.email})
    if(existing_user != None):
        return JSONResponse(status_code=404,content={"message":"Please enter another email address","success":False})
    encoded_password = user.password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password,bcrypt.gensalt(10))
    collection.insert_one({"username":user.username,"email":user.email,"password": hashed_password,"createdAt":datetime.now().strftime('%d-%m-%Y:%H:%M:%S')})
    userFound = collection.find_one({"email":user.email})
    if(userFound==None):
        return JSONResponse(status_code=500,content={"message":"Internal server error","success":False})
    return JSONResponse(status_code=201,content={"message":"user created successfully","success":True,"data":{"_id":str(userFound["_id"]),"email":userFound["email"],"username":userFound["username"]}})


