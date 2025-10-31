from fastapi import FastAPI
from database import Base, engine
from routers import users , chats, messages , auth

# Create all tables (only runs once at startup)
Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(title="Chat Backend API")

# Register routers
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(auth.router)
app.include_router(users.router)


