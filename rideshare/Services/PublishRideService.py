import json
from fastapi import FastAPI
import Schemas.Schema
import Models.models
from sqlalchemy.orm import Session

from datetime import datetime
import pytz

def correct_date_format(date_str: str):
    """Ensure the date is correctly stored in UTC format."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    return date_obj.date()  # Ensure only date part is stored

def Publish_Ride(Rides: Session, Ride: Schemas.Schema.PublishRide, UserID: int):
    serialized_stopovers = [stopover.dict() for stopover in Ride.stopovers]
    serialized_stopoverFares = [StopOver_Fare.dict() for StopOver_Fare in Ride.StopOver_Fare]

    db_Rides = Models.models.PublishRide(
        UserID=UserID,
        pickup=Ride.pickup, 
        destination=Ride.destination,
        stopovers=serialized_stopovers,
        date=correct_date_format(Ride.date),  # Fix applied here
        time=Ride.time,
        Is_women_only=Ride.Is_women_only,
        Rules_=Ride.Rules_,
        Fare=str(Ride.Fare),
        StopOver_Fare=serialized_stopoverFares,
        Car_Number=Ride.Car_Number,
        Car_Type=Ride.Car_Type,
        No_Of_Seats=Ride.No_Of_Seats,
        instant_booking=Ride.instant_booking
    )

    try:
        Rides.add(db_Rides)
        Rides.commit()
        Rides.refresh(db_Rides)
        return db_Rides
    except Exception as e:
        Rides.rollback()
        raise Exception(f"Failed to publish ride: {e}")

def get_rides_by_userid(Rides: Session, UserID: int):
    return Rides.query(Models.models.PublishRide).filter(UserID == Models.models.PublishRide.UserID).all()

def get_stopovers_by_rideid(Rides: Session, RideID: int):
    return Rides.query(Models.models.PublishRide).filter(RideID == Models.models.PublishRide.id).all()


