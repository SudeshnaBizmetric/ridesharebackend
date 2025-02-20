from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "users"  # Ensure this matches in all cases
    id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(50))
    E_mail = Column(String(50), unique=True, index=True)
    Phone_number = Column(String(10), unique=True)
    password = Column(String(255))

    # Relationships
    publishrides = relationship("PublishRide", back_populates="user", lazy="select")
    bookings = relationship("Bookings", back_populates="user", lazy="select")
    requests = relationship("RideRequest", back_populates="user", lazy="select")
    userinformation = relationship("UserInformation", back_populates="user", lazy="select")
    profile_picture = relationship("ProfilePicture", back_populates="user", uselist=False)
    
class PublishRide(Base):
    __tablename__ = "publishedrides"  
    id = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id')) 
    pickup = Column(String(80))
    destination = Column(String(80))
    stopovers = Column(JSON, nullable=False)
    date = Column(String(30))
    time = Column(String(50))
    Is_women_only = Column(Boolean)
    Rules_ = Column(String(1000))
    Fare = Column(String(50))
    StopOver_Fare = Column(JSON, nullable=False)
    Car_Number = Column(String(50),unique=True)
    Car_Type = Column(String(50))
    No_Of_Seats = Column(Integer)
    instant_booking = Column(Boolean, default=False)
    # Relationships
    user = relationship("Users", back_populates="publishrides")
    bookings = relationship("Bookings", back_populates="ride", lazy="select")
    requests = relationship("RideRequest", back_populates="publishrides", lazy="select")

class Bookings(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id'))
    RideID = Column(Integer, ForeignKey('publishedrides.id'))
    Seats_Booked = Column(Integer)
    booking_status = Column(Boolean, default=False, nullable=False)
    seats_remaining = Column(Integer)
    # Relationships
    user = relationship("Users", back_populates="bookings")
    ride = relationship("PublishRide", back_populates="bookings")

class RideRequest(Base):
    __tablename__ = "riderequests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id'))  # Reference to the user making the request
    RideID = Column(Integer, ForeignKey('publishedrides.id'))  # Reference to the ride being requested
    Seats_Requested = Column(Integer, nullable=False)  # Number of seats requested
   
    

    # Relationships
    user = relationship("Users", back_populates="requests")  # Relationship with Users
    publishrides = relationship("PublishRide", back_populates="requests")  # Relationship with PublishRide




class UserInformation(Base):
    __tablename__ = "userextrainformation"  
    id = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('users.id')) 
    About = Column(String(1000))
    Vehicle = Column(String(50))
    Travel_Preference_Music = Column(String(50))
    Travel_Preference_Pets = Column(String(50))
    Travel_Preference_Smoking = Column(String(50))
    Travel_Preference_Conversation = Column(String(50))
    isposted = Column(Boolean, default=False)
    # Relationships
    user = relationship("Users", back_populates="userinformation")

from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class ProfilePicture(Base):
    __tablename__ = "profile_pictures"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)  # Foreign key to Users table
    image_path = Column(String(255), nullable=False)  # Path or URL to the image

    user = relationship("Users", back_populates="profile_picture")  # Relationship with Users

