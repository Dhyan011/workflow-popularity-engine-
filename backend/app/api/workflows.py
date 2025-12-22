from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.workflow import Workflow
from backend.app.schemas.workflow import WorkflowOut, PopularityMetrics

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"]
)

@router.get(
    "/top",
    response_model=list[WorkflowOut]
)
def get_top_workflows(
    platform: str = Query(..., example="youtube"),
    country: str = Query(..., example="IN"),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Workflow)
        .filter(
            Workflow.platform == platform,
            Workflow.country == country
        )
        .order_by(Workflow.popularity_score.desc())
        .limit(limit)
        .all()
    )

    results = []
    for w in rows:
        results.append(
            WorkflowOut(
                workflow=w.workflow_name,
                platform=w.platform,
                country=w.country,
                popularity_score=w.popularity_score,
                popularity_metrics=PopularityMetrics(
                    views=w.views,
                    likes=w.likes,
                    comments=w.comments,
                    like_to_view_ratio=w.like_to_view_ratio,
                    comment_to_view_ratio=w.comment_to_view_ratio,
                )
            )
        )

    return results