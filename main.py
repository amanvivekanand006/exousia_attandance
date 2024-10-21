from fastapi import FastAPI,Query,HTTPException
from pydantic import BaseModel,EmailStr
from pymongo import MongoClient
from enum import Enum
from datetime import datetime,time,timedelta, date
from typing import Optional
from passlib.context import CryptContext
from urllib.parse import quote_plus
import calendar
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,  # Allows credentials (such as cookies, authorization headers, etc.) to be sent in cross-origin requests
    allow_methods=["*"],  # Allows all methods (such as GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"]
)

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
    counter = user_collection.find_one_and_update(
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
        "employee_id": emp_id,
        "creation_date_time":datetime.now(),
        "password" : get_password_hash(user.password),
        "confirm_password" : get_password_hash(user.confirm_password),
    })
    if user_collection.find_one({"email":user.email}):
        raise HTTPException(status_code=400, detail="Email Id Already Exist")
    
    elif (user.password != user.confirm_password):
        raise HTTPException(status_code=400, detail="Password and Confirm Password does not match")

    else:
        user_collection.insert_one(document)
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return {"message": "Registration successfull", "user":document}



@app.patch("/update_admin_status", tags=["AdminRegistration"])
def update_status(userid:str, status : str = Query(...,enum=["Active","Inactive"])):
    if (user_collection.find_one({"employee_id":userid})):
        document = user_collection.find_one_and_update({"employee_id":userid} , {"$set":{"status":status}},return_document=True)
        document["_id"] = str(document["_id"])
        return document
    else:
        raise HTTPException(status_code=404, detail = "User Not Found")


@app.get("/get_all_active_admin", tags=["AdminRegistration"])
def get_all_active_user():
    documents = user_collection.find({"status":"Active","role":"admin"})
    active_admins = []
    for doc in documents:
       doc["_id"] = str(doc["_id"])
       active_admins.append(doc)
    return active_admins

@app.get("/get_all_admin", tags=["AdminRegistration"])
def get_all_user():
    documents = list(user_collection.find({"role":"admin"}))
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
    elif user_collection.find_one({"email":user.email}):
        raise HTTPException(status_code=400, detail="Email Id Already Exist")
    else:
        user_collection.insert_one(document)
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        return {"message": "Registration successfull", "user":document}

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
    documents = user_collection.find({"status":"Active", "role":"employee"})
    active_users = []
    for doc in documents:
       doc["_id"] = str(doc["_id"])
       active_users.append(doc)
    return active_users

@app.get("/get all users", tags=["UserRegistration"])
def get_all_user():
    documents = list(user_collection.find({"role":"employee"}))
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents




#-----------------------------------------------------user login------------------------------------------------------#



class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@app.post("/User_login", tags=["User_and admin_Login"])
def login(user: LoginSchema):
    db_user = user_collection.find_one({"email": user.email, "status":"Active"})
    if db_user and verify_password(user.password, db_user['password']):
        return {"message": "Login successful", "user_id": str(db_user["employee_id"]), "role":db_user["role"], "name":db_user["name"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or InActive User!")
    

#------------------------------------------------------------admin login--------------------------------------------------------------------#
# @app.post("/admin_login", tags=["Admin Login"])
# def login(user: LoginSchema):
#     db_user = admin_collection.find_one({"email": user.email})
#     if db_user and verify_password(user.password, db_user['password']):
#         return {"message": "Login successful", "user_id": str(db_user["admin_id"])}
#     else:
#         raise HTTPException(status_code=401, detail="Invalid credentials")



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
    

#----------------------------------------------get api for tables----------------------------------------------------------------------------#



@app.get("/get_one_employee_punching_details")
def get_emp_datails(usedid:str , date: Optional[date]):
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    document = user_punch_col.find_one({
        "employee_id": usedid,
        "date_and_time": {"$gte": start_of_day, "$lt": end_of_day}
    })
    document["_id"] = str(document["_id"])
    return document

@app.get("/get_all_employee_punching_details")
def get_emp_datails(date: Optional[date]):
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    documents = user_punch_col.find({
        "date_and_time": {"$gte": start_of_day, "$lt": end_of_day}
    })
    emp_punches = []
    for doc in documents:
      doc["_id"] = str(doc["_id"])
      emp_punches.append(doc)
    return emp_punches






#---------------------------------------------------get_one_emp_attandance_details-------------------------------------------------------#

def calculate_working_hours(punch_in, punch_out):
    # Calculate total worked hours for the day
    if punch_in and punch_out:
        time_diff = punch_out - punch_in
        return time_diff.total_seconds() / 3600  # Convert seconds to hours
    return 0

def get_current_month_range():
    # Get today's date
    today = datetime.today()

    # First day of the current month
    start_date = today.replace(day=1)

    # Last day of the current month
    last_day = calendar.monthrange(today.year, today.month)[1]  # Get the number of days in the month
    end_date = today.replace(day=last_day)

    return start_date, end_date

@app.get("/employee_attendance")
def get_employee_attendance(employee_id: str):
    # Get current month start and end date
    start_date, end_date = get_current_month_range()

    # Fetch all records for the employee within the month
    records = list(user_punch_col.find({
        "employee_id": employee_id,
        "punch_in_time": {"$gte": start_date, "$lt": end_date}
    }))

    # Initialize counters
    full_days = 0
    half_days = 0
    leaves = 0

    # Define full day and half day limits (in hours)
    full_day_hours = 9
    half_day_hours = 4

    # Track all dates where the employee has records
    tracked_dates = set()

    for record in records:
        punch_in_time = record.get("punch_in_time")
        punch_out_time = record.get("punch_out_time")
        date = punch_in_time.date()

        tracked_dates.add(date)
        working_hours = calculate_working_hours(punch_in_time, punch_out_time)

        if working_hours >= full_day_hours:
            full_days += 1
        elif half_day_hours <= working_hours < full_day_hours:
            half_days += 1

    # Calculate leaves by finding dates without any punch-in records
    total_days = (end_date - start_date).days + 1
    leaves = total_days - len(tracked_dates)

    return {
        "employee_id": employee_id,
        "full_days": full_days,
        "half_days": half_days,
        "leaves": leaves
    }







#-------------------------------get_all_emp_attandance_details------------------------------------------------------------------#



def cal_all_emp_working_hours(punch_in_time, punch_out_time):
    if punch_out_time and punch_in_time:
        return (punch_out_time - punch_in_time).seconds / 3600  # Convert seconds to hours
    return 0

# Helper function to get the start and end date of the current month
def get_current_month_range():
    today = datetime.today()

    # First day of the current month
    start_date = today.replace(day=1)

    # Last day of the current month
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day)

    return start_date, end_date

# Get all employee attendance details
@app.get("/all_employee_attendance")
def get_all_employee_attendance():
    start_date, end_date = get_current_month_range()

    # Fetch all employees
    all_employees = list(user_collection.find({}))

    result = []

    # Iterate through each employee
    for employee in all_employees:
        if "employee_id" not in employee:
          continue
        # Fetch the employee_id and proceed with the attendance logic
        employee_id = employee["employee_id"]

        # Fetch attendance records for the current employee within the current month
        records = list(user_punch_col.find({
            "employee_id": employee_id,
            "punch_in_time": {"$gte": start_date, "$lt": end_date}
        }))

        # Initialize counters
        full_days = 0
        half_days = 0
        leaves = 0
        full_day_hours = 9
        half_day_hours = 4

        tracked_dates = set()

        for record in records:
            punch_in_time = record.get("punch_in_time")
            punch_out_time = record.get("punch_out_time")
            date = punch_in_time.date()

            tracked_dates.add(date)
            working_hours = cal_all_emp_working_hours(punch_in_time, punch_out_time)

            if working_hours >= full_day_hours:
                full_days += 1
            elif half_day_hours <= working_hours < full_day_hours:
                half_days += 1

        # Calculate leaves (total days in the month - days with records)
        total_days = (end_date - start_date).days + 1
        leaves = total_days - len(tracked_dates)

        # Append employee attendance details to the result list
        result.append({
            "employee_id": employee_id,
            "name": employee["name"],
            "full_days": full_days,
            "half_days": half_days,
            "leaves": leaves
        })

    return result