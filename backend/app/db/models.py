from sqlalchemy import Column, String, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String, nullable=False)  # timestamptz
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    
    # Relationships
    knowledge_stores = relationship("KnowledgeStore", back_populates="user")
    threads = relationship("Thread", back_populates="user")
    tokens = relationship("Token", back_populates="user")

class KnowledgeStore(Base):
    __tablename__ = "knowledge_stores"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String, nullable=False)  # timestamptz
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_name = Column(String, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="knowledge_stores")
    files = relationship("File", back_populates="knowledge_store")
    threads = relationship("Thread", back_populates="knowledge_store")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String, nullable=False)  # timestamptz
    store_id = Column(Integer, ForeignKey("knowledge_stores.id"), nullable=False)
    source = Column(String, nullable=False)  # TODO: Update Type
    
    # Relationships
    knowledge_store = relationship("KnowledgeStore", back_populates="files")

class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String, nullable=False)  # timestamptz
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("knowledge_stores.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="threads")
    knowledge_store = relationship("KnowledgeStore", back_populates="threads")
    messages = relationship("Message", back_populates="thread")

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(String, nullable=False)  # timestamptz
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_authenticator = Column(String, nullable=False)  # TODO: Update Type
    # Relationships
    user = relationship("User", back_populates="tokens")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(String, nullable=False)  # timestamptz
    
    # Relationships
    thread = relationship("Thread", back_populates="messages")
