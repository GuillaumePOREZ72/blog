from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

from ..models.user import User, UserCreate, UserUpdate, UserResponse
from .database import database


class UserService:
    """"""