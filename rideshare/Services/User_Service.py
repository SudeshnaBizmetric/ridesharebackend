import Models.models
import Schemas.Schema
from sqlalchemy.orm import Session
def create_user(users:Session,user:Schemas.Schema.Users):
    db_user=Models.models.Users(
        id=user.id,
        Name=user.Name,
        E_mail=user.E_mail,
        Phone_number=user.Phone_number,
        password=user.password
    )

    users.add(db_user)
    users.commit()
    users.refresh(db_user)
    return db_user

def get_user_by_mail(users:Session,email:str):
    return users.query(Models.models.Users).filter(email==Models.models.Users.E_mail).first()

def get_user(users: Session, id: int):
    return users.query(Models.models.Users).filter(Models.models.Users.id==id).first()

def save_user_extra_details( user:Session,user_info:Schemas.Schema.UserInformation,UserID:int):

    db_user_info=Models.models.UserInformation(
        UserID=UserID,
        About=user_info.About,
        Vehicle=user_info.Vehicle,
        Travel_Preference_Music=user_info.Travel_Preference_Music,
        Travel_Preference_Pets=user_info.Travel_Preference_Pets,
        Travel_Preference_Smoking=user_info.Travel_Preference_Smoking,
        Travel_Preference_Conversation=user_info.Travel_Preference_Conversation,
        isposted=user_info.isposted
    )

    user.add(db_user_info)
    user.commit()
    user.refresh(db_user_info)
    return db_user_info

def get_user_entrainfo(users: Session, id: int):
    return users.query(Models.models.UserInformation).filter(Models.models.UserInformation.UserID==id).first()

def edit_user_extra_details(user:Session,user_extra_info:Schemas.Schema.UserInformation,UserID:int):
    db_user_info=Models.models.UserInformation(
        UserID=UserID,
        About=user_extra_info.About,
        Vehicle=user_extra_info.Vehicle,
        Travel_Preference_Music=user_extra_info.Travel_Preference_Music,
        Travel_Preference_Pets=user_extra_info.Travel_Preference_Pets,
        Travel_Preference_Smoking=user_extra_info.Travel_Preference_Smoking,
        Travel_Preference_Conversation=user_extra_info.Travel_Preference_Conversation,
        isposted=user_extra_info.isposted
        
    )

    user.query(Models.models.UserInformation).filter(Models.models.UserInformation.UserID==UserID).update(db_user_info)
    user.commit()
    user.refresh(db_user_info)
    return db_user_info

def deleteuseraccount(users:Session,id:int):
    user=users.query(Models.models.Users).filter(Models.models.Users.id==id).first()
    users.delete(user)
    users.commit()
    return user