from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pymongo import MongoClient
import os
import bcrypt
import uvicorn

client = MongoClient(os.getenv("MONGO_URI"))
db = client.fastapi_userauth
collection = db.users

class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginUser(BaseModel):
    email: EmailStr
    password: str

app = FastAPI()

@app.post("/api/v1/user/create")
def create_user(user:CreateUser):
    existing_user = collection.find_one({"email":user.email})
    # check if user exist with the given email
    if(existing_user != None):
        return JSONResponse(status_code=404,content={"message":"Please enter another email address","success":False})
    
    # hash the provided password
    encoded_password = user.password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password,bcrypt.gensalt(10))

    # save the user in the database
    collection.insert_one({"username":user.username,"email":user.email,"password": hashed_password,"createdAt":datetime.now().strftime('%d-%m-%Y:%H:%M:%S')})

    # check that the user is created successfully or not
    userFound = collection.find_one({"email":user.email})
    if(userFound==None):
        return JSONResponse(status_code=500,content={"message":"Internal server error","success":False})
    
    # if everything works fine
    return JSONResponse(status_code=201,content={"message":"user created successfully","success":True,"data":{"_id":str(userFound["_id"]),"email":userFound["email"],"username":userFound["username"]}})

@app.post("/api/v1/user/login")
def login_user(user:LoginUser):

    # check if any user exists with the given email id
    userFound = collection.find_one({"email":user.email})
    if(userFound == None):
        return JSONResponse(status_code=404,content={"message":"Please enter correct credentials","success":False})
    
    # compare password
    isPasswordCorrect = bcrypt.checkpw(user.password.encode("utf-8"),userFound["password"])
    if(isPasswordCorrect == False):
       return JSONResponse(status_code=404,content={"message":"Please enter correct credentials","success":False})

    # if everything works fine
    return JSONResponse(status_code=200,content={"message":"loggedin successfully","success":True,"data":{"_id":str(userFound["_id"]),"email":userFound["email"],"username":userFound["username"]}})
