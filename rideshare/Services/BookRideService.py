from fastapi import FastAPI, HTTPException
from sqlalchemy import func
import Schemas.Schema
import Models.models
from sqlalchemy.orm import Session


def book_ride_instant(
    Rides: Session, 
    Ride: Schemas.Schema.BookARide, 
    UserID: int, 
    RideID: int, 
    seats: int
):
    try:
        # Fetch the ride details using RideID
        ride_record = Rides.query(Models.models.PublishRide).filter(
            Models.models.PublishRide.id == RideID
        ).first()

        if not ride_record:
            raise HTTPException(status_code=404, detail="Ride not found")

        # Calculate the number of seats already booked
        booked_seats = Rides.query(Models.models.Bookings).filter(
            Models.models.Bookings.RideID == RideID
        ).with_entities(func.sum(Models.models.Bookings.Seats_Booked)).scalar() or 0

        # Calculate remaining seats
        remaining_seats = ride_record.No_Of_Seats - booked_seats

        # Check if enough seats are available
        if remaining_seats < seats:
            raise HTTPException(status_code=400, detail="Not enough seats available")

        
        db_Rides = Models.models.Bookings(
            UserID=UserID,
            RideID=RideID,
            Seats_Booked=seats,
            booking_status=True,
            seats_remaining=remaining_seats - seats  
        )
        
        
        ride_record.booked_seats = booked_seats + seats
        Rides.commit()

        # Add the new booking
        Rides.add(db_Rides)
        Rides.commit()
        Rides.refresh(db_Rides)
        
        return db_Rides

    except AttributeError as e:
        raise HTTPException(status_code=400, detail="Attribute error: Check input data")
    except Exception as e:
        Rides.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to book ride: {e.__class__.__name__} - {str(e)}"
        )


def request_ride(
    db_session: Session,
    ride_request: Schemas.Schema.RequestRide,
    UserID: int,
):
    print("Received ride request:", ride_request)
    try:
        # Fetch the ride details using the RideID from the `PublishRide` table
        ride_record = db_session.query(Models.models.PublishRide).filter(
            Models.models.PublishRide.id == ride_request.RideID
        ).first()

        if not ride_record:
            raise HTTPException(status_code=404, detail="Ride not found")

        # Ensure the user is not requesting their own ride
        if ride_record.UserID == UserID:
            raise HTTPException(
                status_code=400, detail="Cannot request your own published ride"
            )

        # Create a new request ride record
        db_request_ride = Models.models.RideRequest(
            UserID=UserID,
            RideID=ride_request.RideID,
            Seats_Requested=ride_request.Seats_Requested,
           
        )

        # Save the request to the database
        db_session.add(db_request_ride)
        db_session.commit()
        db_session.refresh(db_request_ride)

        # Optionally, notify the driver about the request (add logic as needed)

        return db_request_ride

    
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to request ride: {e.__class__.__name__} - {str(e)}",
        )


