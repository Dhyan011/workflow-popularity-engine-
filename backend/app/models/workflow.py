from sqlalchemy import Column, Integer, String, Float
from backend.app.db.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)

    workflow_name = Column(String, index=True)
    platform = Column(String, index=True)
    country = Column(String, index=True)

    views = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)

    like_to_view_ratio = Column(Float)
    comment_to_view_ratio = Column(Float)
