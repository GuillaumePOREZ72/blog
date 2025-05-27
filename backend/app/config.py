from motor.motor_asyncio import AsyncIOMotorClient

#Mongo URI
MONGO_URI = "mongodb+srv://porezguillaumegp:R0EC5EIknaY9xgjL@guiguiblog.3thevus.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["GuiguiBlog"]


