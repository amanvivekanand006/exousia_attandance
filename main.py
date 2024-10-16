from fastapi import FastAPI,Query,HTTPException
from pydantic import BaseModel,EmailStr
from pymongo import MongoClient
from enum import Enum
from datetime import datetime,time
from typing import Optional
from passlib.context import CryptContext
from urllib.parse import quote_plus



app = FastAPI()


# username = 'exousiatraining'
# password = 'exousia@123'
# encoded_username = quote_plus(username)
# encoded_password = quote_plus(password)
MONGO_DETAILS="mongodb+srv://exousiatraining:exousia123@cluster0.vkin1.mongodb.net/"
client = MongoClient(MONGO_DETAILS)




#-----------------------------------------------------------Admin Registration-----------------------------------------------------------#

db = client.admin_registration
admin_collection =  db.admin_collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class userschema(BaseModel):
    name : str
    dob : datetime
    email : EmailStr
    password: str
    confirm_password: str
    mobile_number: str
    role : Optional[str] = "admin"
    status : Optional[str] = "Inactive"

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def creating_adminid():
    counter = admin_collection.find_one_and_update(
        {'_id': 'admin_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=True
    )
    return counter['sequence_value']

@app.post("/create_admin", tags=["AdminRegistration"])
def create_user(user:userschema, gender : str = Query(...,enum=["Male","Female"])):
    sequence_value = creating_adminid()
    emp_id = f"AdminID{sequence_value + 1000:04d}"
     
    document = user.dict()
    document.update({
        "Gender":gender,
        "admin_id": emp_id,
        "creation_date_time":datetime.now(),
        "password" : get_password_hash(user.password),
        "confirm_password" : get_password_hash(user.confirm_password),
    })

    if (user.password != user.confirm_password):
        raise HTTPException(status_code=400, detail="Password and Confirm Password does not match")
    else:
        admin_collection.insert_one(document)
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return document



@app.patch("/update_admin_status", tags=["AdminRegistration"])
def update_status(adminid:str, status : str = Query(...,enum=["Active","Inactive"])):
    if (admin_collection.find_one({"admin_id":adminid})):
        document = admin_collection.find_one_and_update({"admin_id":adminid} , {"$set":{"status":status}},return_document=True)
        document["_id"] = str(document["_id"])
        return document
    else:
        raise HTTPException(status_code=404, detail = "User Not Found")


@app.get("/get_all_active_admin", tags=["AdminRegistration"])
def get_all_active_user():
    document = admin_collection.find_one({"status":"Active"})
    document["_id"] = str(document["_id"])
    return document

@app.get("/get_all_admin", tags=["AdminRegistration"])
def get_all_user():
    documents = list(admin_collection.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents




#------------------------------------------------------------------------user registration--------------------------------------------------------------------------------#

db = client.user_registration
user_collection =  db.user_collection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class userschema(BaseModel):
    name : str
    dob : datetime
    email : EmailStr
    password: str
    confirm_password: str
    mobile_number: str
    role : Optional[str] = "employee"
    status : Optional[str] = "Inactive"

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def creating_userid():
    counter = user_collection.find_one_and_update(
        {'_id': 'user_id'},
        {'$inc': {'sequence_value': 1}},
        upsert=True,
        return_document=True
    )
    return counter['sequence_value']



@app.post("/create_user", tags=["UserRegistration"])
def create_user(user:userschema, gender : str = Query(...,enum=["Male","Female"]), domain: str = Query(...,enum=["Python","Web Development","Testing","Devops","Java"])):
    sequence_value = creating_userid()
    emp_id = f"ECES{sequence_value + 1000:04d}"
     
    document = user.dict()
    document.update({
        "Gender":gender,
        "Domain": domain,
        "employee_id": emp_id,
        "creation_date_time":datetime.now(),
        "password" : get_password_hash(user.password),
        "confirm_password" : get_password_hash(user.confirm_password),
    })

    if (user.password != user.confirm_password):
        raise HTTPException(status_code=400, detail="Password and Confirm Password does not match")
    else:
        user_collection.insert_one(document)
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return document

@app.patch("/update_status", tags=["UserRegistration"])
def update_status(userid:str, status : str = Query(...,enum=["Active","Inactive"])):
    if (user_collection.find_one({"employee_id":userid})):
        document = user_collection.find_one_and_update({"employee_id":userid} , {"$set":{"status":status}},return_document=True)
        document["_id"] = str(document["_id"])
        return document
    else:
        raise HTTPException(status_code=404, detail = "User Not Found")
    

@app.get("/get all active users", tags=["UserRegistration"])
def get_all_active_user():
    document = user_collection.find_one({"status":"Active"})
    document["_id"] = str(document["_id"])
    return document

@app.get("/get all users", tags=["UserRegistration"])
def get_all_user():
    documents = list(user_collection.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents




#-----------------------------------------------------user login------------------------------------------------------#



class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@app.post("/User login", tags=["User Login"])
def login(user: LoginSchema):
    db_user = user_collection.find_one({"email": user.email})
    if db_user and verify_password(user.password, db_user['password']):
        return {"message": "Login successful", "user_id": str(db_user["employee_id"])}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

#------------------------------------------------------------admin login--------------------------------------------------------------------#
@app.post("/admin login", tags=["Admin Login"])
def login(user: LoginSchema):
    db_user = admin_collection.find_one({"email": user.email})
    if db_user and verify_password(user.password, db_user['password']):
        return {"message": "Login successful", "user_id": str(db_user["admin_id"])}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")



#----------------------------------------------------------User Puchin-----------------------------------------------------------------#

db = client.user_punching
user_punch_col =  db.user_login_logout_collection

class punch_in_schema(BaseModel):
    date_and_time : Optional[datetime] = datetime.now().isoformat()


@app.post("/PunchIn", tags=["User_punchingtime"])
def user_punch_time(userid:str,punchschema:punch_in_schema):
     # Check if user exists
    user_data = user_collection.find_one({"employee_id": userid})
    if not user_data:
        raise HTTPException(status_code=404, detail="Invalid User")
    
    # Get the current date and time
    now = datetime.now()
    today_start = datetime.combine(now.date(), time.min)
    today_end = datetime.combine(now.date(), time.max)
    
    # Check if the user has already punched in today
    existing_punch = user_punch_col.find_one({
        "employee_id": userid,
        "punch_in_time": {"$gte": today_start, "$lt": today_end}
    })
    
    if existing_punch:
        raise HTTPException(status_code=400, detail="User has already punched in today")
    
    # Insert the punch-in record
    punch_details = punchschema.dict()
    punch_details.update({
        "employee_id": userid,
        "punch_in_time": punchschema.date_and_time
    })
    
    # Combine punch-in details with user data
    combined_data = {**user_data, **punch_details}
    
    # Insert combined data into the user_punch_col collection
    result = user_punch_col.insert_one(combined_data)
    combined_data["_id"] = str(result.inserted_id)
    
    return {"message": "Punch-In Successful", "punch_details": combined_data}

@app.post("/PunchOut", tags=["User_punchingtime"])
def user_punch_time(userid:str,punchschema:punch_in_schema):
    # Check if user exists
    user_data = user_collection.find_one({"employee_id": userid})
    if not user_data:
        raise HTTPException(status_code=404, detail="Invalid User")

    # Get the current date and time
    now = datetime.now()
    today_start = datetime.combine(now.date(), time.min)
    today_end = datetime.combine(now.date(), time.max)
    
    # Check if the user has punched in today
    existing_punch_in = user_punch_col.find_one({
        "employee_id": userid,
        "punch_in_time": {"$gte": today_start, "$lt": today_end}
    })
    
    if not existing_punch_in:
        raise HTTPException(status_code=400, detail="No Punch-In record found for today")
    
    # Check if the user has already punched out today
    existing_punch_out = user_punch_col.find_one({
        "employee_id": userid,
        "punch_out_time": {"$gte": today_start, "$lt": today_end}
    })
    
    if existing_punch_out:
        raise HTTPException(status_code=400, detail="User has already punched out today")
    
    # Insert or update the punch-out record
    punch_details = punchschema.dict()
    punch_details.update({
        "employee_id": userid,
        "punch_out_time": now  # Ensure to set the current punch-out time
    })
    
    # Update the punch-out time for the existing punch-in record
    result = user_punch_col.update_one(
        {"employee_id": userid, "punch_in_time": {"$gte": today_start, "$lt": today_end}},
        {"$set": {"punch_out_time": now}},
        upsert=False
    )
    
    # Check if the update was successful
    if result.matched_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update Punch-Out record")
    
    # Fetch the updated punch-out record
    updated_punch_record = user_punch_col.find_one({
        "employee_id": userid,
        "punch_out_time": now
    })
    
    updated_punch_record["_id"] = str(updated_punch_record["_id"])  # Convert ObjectId to string
    
    return {"message": "Punch-Out Successful", "punch_details": updated_punch_record}
    
