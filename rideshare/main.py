import datetime
from pathlib import Path
from sqlalchemy import or_
from typing import List ,Optional
from fastapi import Depends, FastAPI ,HTTPException ,File, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
import Models.models 
import Services.BookRideService
import Services.PublishRideService
import Services.User_Service
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from Schemas import Schema
import auth
from database import Base ,engine ,Local_Session
from passlib.context import CryptContext
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from Models.models import Users
from sqlalchemy import and_, cast, Date
from Models.models import PublishRide
from sqlalchemy.sql import func
import shutil
from sqlalchemy.sql import text
import os
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()    #fastapi instance
Base.metadata.create_all(bind=engine)   #to connect with database 
password_crypt=CryptContext(schemes=["bcrypt"],deprecated="auto")  #for password hashing


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lively-hill-01625d700.6.azurestaticapps.net"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

def hashed_password(password:str)->str:
   return password_crypt.hash(password)

def get_db():
    db=Local_Session()

    try:
       yield db
    finally:
       db.close()


#Registration API 

@app.post("/v1/users",response_model=Schema.Users,status_code=201)
def add_new_user(user:Schema.Users,users:Session=Depends(get_db)):
   user.password = hashed_password(user.password)
   new_user=Models.models.Users(
      Name=user.Name,
      E_mail=user.E_mail,
      Phone_number=user.Phone_number,
      password=user.password
   )
   users.add(new_user)
   users.commit()
   users.refresh(new_user)
   return new_user

   
@app.post("/v1/login") 
def LoginUser(login:Schema.Login,users:Session=Depends(get_db)):
     user=Services.User_Service.get_user_by_mail(users,login.E_mail)

     if not user:
         raise  HTTPException (status_code=401,detail="Invalid Credentials")
     if (login.password==user.password):
         raise  HTTPException (status_code=401,detail="Invalid Credentials")
     access_token=auth.create_access_token(data={"id":user.id})
     return {"access_token": access_token, "id": user.id}


def get_current_user(
    token: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> Users:
    try:
        # Decode the token
        payload = jwt.decode(token.credentials, auth.secret, algorithms=auth.algorithm)
        user_id: int = payload.get("id")  # Extract the user ID
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: Missing user ID")
        
        # Query the user in the database
        user = db.query(Users).filter(Users.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.post("/v1/publishrides", response_model=Schema.PublishRide, status_code=201)
def publish_rides(ride_data: Schema.PublishRide, rides: Session = Depends(get_db),current_userid:Models.models.Users= Depends(get_current_user)):
 
    try:
        # Use the service layer to handle ride creation logic
        ride = Services.PublishRideService.Publish_Ride(rides, ride_data,UserID=current_userid.id)
        
        # Database operations
        rides.add(ride)
        rides.commit()
        rides.refresh(ride)
        return ride
    except Exception as e:
      rides.rollback()
      raise HTTPException(
        status_code=400,
        detail=f"Failed to publish ride: {str(e)}"
)
    
@app.get("/v1/publishrides/{UserID}")
def get_rides_by_userid(UserID:int,rides:Session=Depends(get_db)):
    return Services.PublishRideService.get_rides_by_userid(rides,UserID)

@app.get("/v1/users/{id}")
def get_user(id:int,users:Session=Depends(get_db)):
    return Services.User_Service.get_user(users,id)

@app.post("/v1/userextrainformation/{UserID}",response_model=Schema.UserInformation,status_code=201)
def save_user_extra_details(user_info:Schema.UserInformation,users:Session=Depends(get_db),current_userid:Models.models.Users= Depends(get_current_user)):
    user_info.UserID=current_userid.id
    user_info=Services.User_Service.save_user_extra_details(users,user_info,current_userid.id)
    return user_info

@app.get("/v1/users_extra_info/{id}")
def get_user_entrainfo(id:int,users:Session=Depends(get_db)):
    return Services.User_Service.get_user_entrainfo(users,id)

from fastapi import HTTPException

@app.get("/v1/search-rides")
def search_rides(
    pickup: str,
    destination: str,
    date: str,
    no_of_seats: int,
    db: Session = Depends(get_db)
):
    # date comparison matches only the date portion of a datetime
    rides = db.query(PublishRide).filter(
        PublishRide.pickup.ilike(f"%{pickup}%"),  
        PublishRide.destination.ilike(f"%{destination}%"),  
        text("CAST(date AS DATE) = :date").params(date=date),   
        PublishRide.No_Of_Seats >= no_of_seats  
    ).all()
    
    
    
    if not rides:
        return {"message": "No rides found.", "rides": []}

    
    ride_details = [
        {
            "ride_id": ride.id,
            "UserID" :ride.UserID, 
            "pickup": ride.pickup,
            "destination": ride.destination,
            "date": ride.date,
            "No_Of_Seats": ride.No_Of_Seats,
            "Fare": ride.Fare,
            "Car_Type": ride.Car_Type,
            "Car_Number": ride.Car_Number,
            "stopovers": ride.stopovers,
            "StopOver_Fare": ride.StopOver_Fare,
            "time": ride.time,
            "instant_booking": ride.instant_booking,
        }
        for ride in rides
    ]

    return {"message": "Rides found.", "rides": ride_details}
 
     
 
     
    

@app.post("/v1/bookings_instant", response_model=Schema.BookARide, status_code=201)
def book_ride(
    booking_data: Schema.BookARide, 
    rides: Session = Depends(get_db), 
    current_user: Models.models.Users = Depends(get_current_user)
):
    try:
        # Fetch the ride details using RideID
        ride_record = rides.query(Models.models.PublishRide).filter(
            Models.models.PublishRide.id == booking_data.RideID
        ).first()

        if not ride_record:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        if ride_record.UserID == current_user.id:
            raise HTTPException(
                status_code=400, 
                detail="You cannot book a ride that you have published."
            )

        if ride_record.Seats_Remaining == 0:
            raise HTTPException(
                status_code=400, 
                detail="No seats available for this ride."
            )

        if ride_record.Seats_Remaining < booking_data.Seats_Booked:
            raise HTTPException(
                status_code=400, 
                detail=f"Only {ride_record.Seats_Remaining} seat(s) are available."
            )

        # Call the booking service to process the booking
        booking = Services.BookRideService.book_ride_instant(
            rides, 
            booking_data, 
            UserID=current_user.id, 
            RideID=booking_data.RideID, 
            seats=booking_data.Seats_Booked  # Pass the number of seats requested by the user
        )
        
        return booking

    except HTTPException as e:
        raise e
    except Exception as e:
        rides.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing booking: {str(e)}"
        )

@app.post("/v1/requestrides", response_model=Schema.RequestRide, status_code=201)
def request_rides( 
    booking_data: Schema.RequestRide, 
    rides: Session = Depends(get_db), 
    current_user: Models.models.Users = Depends(get_current_user)
):
    try:
        print("Received booking data:", booking_data)
        # Fetch the ride details using RideID
        ride_record = rides.query(Models.models.PublishRide).filter(
            Models.models.PublishRide.id == booking_data.RideID
        ).first()

        if not ride_record:
            raise HTTPException(status_code=404, detail="Ride not found")

         # Prevent the user from requesting their own ride
        if ride_record.UserID == current_user.id:
            raise HTTPException(
                status_code=400, 
                detail="You cannot request a ride that you have published."
            )

        # Call the booking service to process the booking
        booking = Services.BookRideService.request_ride(
            rides, 
            ride_request=booking_data, 
            UserID=current_user.id
        )
        
        return booking
    except HTTPException as e:
        raise e
    except Exception as e:
        rides.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to request ride: {str(e)}"
        )


@app.get("/v1/rides/{driver_id}/requests", response_model=List[dict])
def get_requests_for_driver(driver_id: int, db: Session = Depends(get_db)):
    """
    Fetch all ride requests for rides published by a specific driver.
    """
    # Query the RideRequest table with necessary joins
    ride_requests = (
        db.query(Models.models.RideRequest)
        .join(PublishRide, PublishRide.id == Models.models.RideRequest.RideID)
        .filter(PublishRide.UserID == driver_id)
        .all()
    )
    print("dricerid",driver_id)
    # If no requests are found, return an empty list
    if not ride_requests:
        return []

    # Serialize the data manually or use a Pydantic model for response
    return [
        {
            "request_id": request.id,
            "ride_id": request.RideID,
            "user_id": request.UserID,
            "seats_requested": request.Seats_Requested,
        }
        for request in ride_requests
    ]

@app.get("/v1/ride-requests/{ride_id}")
def get_ride_requests(ride_id: int, db: Session = Depends(get_db), current_user: Models.models.Users = Depends(get_current_user)):
    # Fetch the ride details to check if the current user is the ride owner
    ride = db.query(Models.models.PublishRide).filter_by(id=ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Ensure only the owner of the ride can view its requests
    if ride.UserID != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden to view these requests")

    # Fetch all requests for the ride
    requests = db.query(Models.models.RideRequest).filter_by(RideID=ride_id).all()

    return requests


@app.delete("/v1/deletebooking/{booking_id}")
def deletebooking(booking_id: int, rides: Session = Depends(get_db)):
    request = rides.query(Models.models.Bookings).filter(Models.models.Bookings.id == booking_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Booking not found.")
    rides.delete(request)
    rides.commit()
    return {"message": "Booking deleted successfully."}

@app.delete("/v1/deleteride/{ride_id}")
def deleteride(ride_id: int, rides: Session = Depends(get_db)):
    request = rides.query(Models.models.PublishRide).filter(Models.models.PublishRide.id == ride_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Ride not found.")
    rides.delete(request)
    rides.commit()
    return {"message": "Ride deleted successfully."}

@app.put("/v1/userextrainformation/{UserID}")
def edit_user_extra_details(user_info:Schema.UserInformation,users:Session=Depends(get_db),current_userid:Models.models.Users= Depends(get_current_user)):
    user_info.UserID=current_userid.id
    user_info=Services.User_Service.edit_user_extra_details(users,user_info,current_userid.id)
    return user_info

@app.get("/v1/bookeduserinfo/{id}")
def getbookeduserinfo(id: int, db: Session = Depends(get_db)):
    user = db.query(Models.models.Users).filter(Models.models.Users.id == id).first()
    if not user:
        return {"message": "User not found"}  # Return a proper response if user is null
    return user

@app.get("/v1/bookeduserextrainfo/{id}")
def getbookeduserinfo(id: int, db: Session = Depends(get_db)):
    user = db.query(Models.models.UserInformation).filter(Models.models.UserInformation.UserID == id).first()
    if not user:
        return {"message": "User not found"}  # Return a proper response if user is null
    return user

@app.get("/v1/rideid")
def get_booking_id(id: int, db: Session = Depends(get_db)):  # Accept id as a query parameter
    booking = db.query(Models.models.Bookings).filter(Models.models.Bookings.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking ID not found")
    return booking

@app.post("/upload-profile-picture/{user_id}")
async def upload_profile_picture(user_id: int, file: UploadFile = File(), db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Define file path
    file_path = Path(UPLOAD_FOLDER) / f"{user_id}_{file.filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check if profile picture entry exists
    profile_picture = db.query(Models.models.ProfilePicture).filter(Models.models.ProfilePicture.user_id == user_id).first()
    
    if profile_picture:
        # Remove old file before updating (if exists)
        if os.path.exists(profile_picture.image_path):
            os.remove(profile_picture.image_path)
        profile_picture.image_path = str(file_path)  # Update existing record
    else:
        new_profile_picture = Models.models.ProfilePicture(user_id=user_id, image_path=str(file_path))
        db.add(new_profile_picture)

    db.commit()
    
    return {"message": "Profile picture uploaded successfully", "profile_picture": str(file_path)}

@app.get("/user/{user_id}/profile-picture")
def get_user_profile_picture(user_id: int, db: Session = Depends(get_db)):
    profile_picture = db.query(Models.models.ProfilePicture).filter(Models.models.ProfilePicture.user_id == user_id).first()
    
    if not profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")

    # Return image file
    return FileResponse(profile_picture.image_path, media_type="image/jpeg")

@app.delete("/v1/deleteuser/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}