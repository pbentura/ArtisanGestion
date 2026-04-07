from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    prenom = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    mdp = Column(String, nullable=True)
    role = Column(String, default="USER", nullable=True)

    societes = relationship("Societe", back_populates="user")
    clients = relationship("Client", back_populates="user")
    rapports = relationship("Rapport", back_populates="user")
