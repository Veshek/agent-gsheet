from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)

    conversations = relationship("Conversations", order_by="Conversations.id", back_populates="user")

class Conversations(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)  # Unique conversation ID
    name = Column(String, nullable=False)  # Name of the conversation
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # Foreign key to User

    user = relationship("User", back_populates="conversations")  # Relationship to User