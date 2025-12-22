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
    platform: str = Query(..., description="youtube | discourse | google"),
    country: str = Query(..., description="US | IN | global"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    workflows = (
        db.query(Workflow)
        .filter(
            Workflow.platform == platform,
            Workflow.country == country
        )
        .order_by(Workflow.popularity_score.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        WorkflowOut(
            workflow=wf.workflow_name,
            platform=wf.platform,
            country=wf.country,
            popularity_metrics=PopularityMetrics(
                views=wf.views,
                likes=wf.likes,
                comments=wf.comments,
                like_to_view_ratio=wf.like_to_view_ratio,
                comment_to_view_ratio=wf.comment_to_view_ratio,
                popularity_score=wf.popularity_score,
            )
        )
        for wf in workflows
    ]