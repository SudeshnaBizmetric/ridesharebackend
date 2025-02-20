from enum import Enum
from typing import Optional ,List
from pydantic import BaseModel, EmailStr, Field

class Users(BaseModel):
    
    Name: str = Field(..., min_length=3, max_length=50)  
    E_mail: EmailStr
    Phone_number: str = Field(..., min_length=10, max_length=10) 
    password: str = Field(..., min_length=8)  

    class Config:
        orm_mode = True

class Login(BaseModel):
    E_mail:EmailStr
    password:str = Field(..., min_length=8)

class StopoverType(BaseModel):
    text: str

class StopoverFareType(BaseModel):
    price: str

class PublishRide(BaseModel):
    UserID:int
    pickup: str
    destination: str
    stopovers:Optional[List[StopoverType] ] 
    date: str
    time: str
    Is_women_only: bool
    Rules_: Optional[str] = None 
    Fare: int
    StopOver_Fare:Optional[List[StopoverFareType] ] 
    Car_Number: str
    Car_Type: str
    No_Of_Seats: int
    instant_booking:Optional [bool ]= False

class Config:
        orm_mode = True

class userProfile(BaseModel):
    Name: str
    E_mail: EmailStr
    Phone_number: int

    class Config:
        orm_mode = True

class Stopover(BaseModel):
    stopovers:Optional[List[StopoverType] ] 

class Config:
        orm_mode = True  

class UserInformation(BaseModel):
    UserID:int
    About: str
    Vehicle: str
    Travel_Preference_Music: str
    Travel_Preference_Pets: str
    Travel_Preference_Smoking: str
    Travel_Preference_Conversation: str
    isposted:bool=False

    class Config:
        orm_mode = True

class BookARide(BaseModel):
    UserID:int
    RideID:Optional[int]
    Seats_Booked:int
    booking_status:bool
    seats_remaining:int

    class Config:
        orm_mode = True

class RequestRide(BaseModel):
    UserID: int
    RideID: int
    Seats_Requested:int
    
    class Config:
        orm_mode = True

class ProfilePicture(BaseModel):
    user_id:int
    image_path:str

    class Config:
        orm_mode = True
