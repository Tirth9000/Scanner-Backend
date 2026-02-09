from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from db.base import getCursor

JWT_SECRET = os.getenv('JWT_SECRET')
security = HTTPBearer()

# Protect middleware - verify JWT and return current user
def protect(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Get token from header 
    token = credentials.credentials
    
    try:
        if not JWT_SECRET:
            raise ValueError("JWT_SECRET not set")
        # Verify token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Get user from the token
        cursor = getCursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (decoded.get("id"),)
        )
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Not authorized, user not found")
        
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2]
        }
        
    except JWTError as error:
        print(error)
        raise HTTPException(status_code=401, detail="Not authorized, token failed")