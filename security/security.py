from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union
import jwt
from jwt import PyJWTError
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import sqlite3
from starlette.status import HTTP_403_FORBIDDEN
import json
import models.models as md

SECRET_KEY = "fca9f70fc9713c56316dba657364f8980be3aba009dac436a5a3fcc319b08c40"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_MINUTES_TIME = timedelta(minutes=2)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
security_basic = HTTPBasic()

users_cli = {
    "devops" : {
        "username": "devops",
        "full_name": "Devops",
        "email": "devops.monitoring@orange.com",
        "password": "$2b$12$yMmznwlf8X4s.J9y8tJlXewnqtd16LYxaiBHNj1VdmKn/MnNduix.", #20.Devops.23
        "disabled": False,
        "admin": False,
        "cli": True,
        "roles": ["user"]
    },
    "admin" : {
        "username": "devops",
        "full_name": "Devops",
        "email": "devops.monitoring@orange.com",
        "password": "$2b$12$yMmznwlf8X4s.J9y8tJlXewnqtd16LYxaiBHNj1VdmKn/MnNduix.", # 
        "disabled": False,
        "admin": True,
        "cli": True,
        "roles": ["admin"]
    }
}
users_db = {
    "devops": {
        "username": "devops",
        "full_name": "Devops",
        "email": "devops.monitoring@orange.com",
        "password": "$2a$12$I6mCdYUtVAoi9tu/Sw9VceLyVjZvYvBGXNoMihSN2OSVh0yWIUrLq", #Enero.2023!
        "disabled": False,
        "admin": False,
        "cli": True,
        "roles": ["user"]
    }
}

users = {
    "devops" : {
        "username": "devops",
        "full_name": "Devops",
        "email": "devops.monitoring@orange.com",
        "password": "$2b$12$yMmznwlf8X4s.J9y8tJlXewnqtd16LYxaiBHNj1VdmKn/MnNduix.", #20.Devops.23
        "disabled": False,
        "admin": True,
        "cli": True,
        "roles": ["user"]
    },
    "admin" : {
        "username": "admin",
        "full_name": "Devops",
        "email": "devops.monitoring@orange.com",
        "password": "$2b$12$yMmznwlf8X4s.J9y8tJlXewnqtd16LYxaiBHNj1VdmKn/MnNduix.", # 
        "disabled": False,
        "admin": True,
        "cli": True,
        "roles": ["admin"]
    }
}



def hash_password(password):
    hash_password = pwd_context.hash(password)
    return hash_password


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return md.UserApi(**user_dict)


def get_user_db(username: str):
    conn = sqlite3.connect('api-db.db')
    conn.row_factory = sqlite3.Row
    query = "SELECT username, full_name, email, password, disabled, admin, cli, role FROM API_USERS WHERE username = '" + username + "'"
    result = conn.execute(query).fetchall()[0]
    conn.close()
    if username == result["username"]:
        return md.UserApi(**result)
    

def authenticate_user(user_db, username: str, password: str):
    user = get_user_db(username)
    #print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = md.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


#### LOGIN SECURITY ####

basic_auth = md.BasicAuth(auto_error=False)
oauth2_scheme2 = md.OAuth2PasswordBearerCookie(tokenUrl="/login_token")


def create_access_token_login(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_login(token: str = Depends(oauth2_scheme2)):
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = md.TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: md.UserApi = Depends(get_current_user_login)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def verify_credentials_basic(credentials: HTTPBasicCredentials = Depends(security_basic), role: str = None):
    user = get_user_db(credentials.username)
    #user = get_user(users, credentials.username)
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"})

    password = verify_password(credentials.password, user.password)
    if not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"})
    
    if not (credentials.username == user.username and password is True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Basic"})
    
    if not user.admin:
        if role != None:
            if role not in user.roles:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="HTTP_401_UNAUTHORIZED",
                                headers={"WWW-Authenticate": "Basic"})

