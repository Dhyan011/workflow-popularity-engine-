from sqlalchemy import Column, Integer, String, Float, Index
from backend.app.db.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)

    # Core identity
    workflow_name = Column(String, index=True)
    platform = Column(String, index=True)          # youtube / forum / google
    source_id = Column(String, index=True)          # videoId, topicId, keyword
    country = Column(String, index=True)

    # Popularity metrics
    views = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)

    like_to_view_ratio = Column(Float)
    comment_to_view_ratio = Column(Float)

    __table_args__ = (
        Index(
            "uq_workflow_source",
            "platform",
            "source_id",
            "country",
            unique=True
        ),
    )