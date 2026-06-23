from fastapi import APIRouter, HTTPException, status, Depends

import database
import schemas
import auth


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: schemas.RegisterRequest):
    existing_user = database.get_user_by_email(data.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = auth.hash_password(data.password)

    database.create_user(
        data.name,
        data.email,
        hashed_password
    )

    return {"message": "User registered successfully"}


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest):
    user = database.get_user_by_email(data.email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not auth.verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = auth.create_token(user["email"])

    return {"token": token}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: dict = Depends(auth.get_current_user)):
    return current_user