from os import getenv
from dotenv import load_dotenv
from googleapiclient.discovery import build
from backend.app.logger import logger
from backend.app.db.database import SessionLocal
from backend.app.models.workflow import Workflow


load_dotenv()

YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def fetch_video_ids(query: str, region: str, max_results: int = 25):
    request = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=max_results,
        regionCode=region,
    )
    response = request.execute()
    return [
        item["id"]["videoId"]
        for item in response.get("items", [])
        if "videoId" in item["id"]
    ]


def fetch_video_stats(video_ids):
    if not video_ids:
        return []

    request = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids),
    )
    response = request.execute()
    return response.get("items", [])


def ingest(region: str):
    logger.info(f"\nStarting YouTube ingestion for region: {region}")
    try:
        db = SessionLocal()

        video_ids = fetch_video_ids("n8n workflow", region)
        videos = fetch_video_stats(video_ids)

        for video in videos:
            video_id = video["id"]
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            existing = (
                db.query(Workflow)
                .filter(
                    Workflow.platform == "youtube",
                    Workflow.source_id == video_id,
                    Workflow.country == region,
                )
                .first()
            )

            if existing:
                existing.workflow_name = snippet.get("title")
                existing.views = views
                existing.likes = likes
                existing.comments = comments
                existing.like_to_view_ratio = (likes / views) if views else 0
                existing.comment_to_view_ratio = (comments / views) if views else 0
                logger.info(f"Updated: {existing.workflow_name}")
            else:
                workflow = Workflow(
                    workflow_name=snippet.get("title"),
                    platform="youtube",
                    source_id=video_id,
                    country=region,
                    views=views,
                    likes=likes,
                    comments=comments,
                    like_to_view_ratio=(likes / views) if views else 0,
                    comment_to_view_ratio=(comments / views) if views else 0,
                )
                db.add(workflow)
                logger.info(
                    f"Inserted: {workflow.workflow_name}",
                    extra={"source_id": video_id, "country": region},
                )

            # IMPORTANT: force constraint checks immediately
            db.flush()

        db.commit()
    except Exception:
        logger.error("Failed to make YouTube ingestion")
        db.rollback()
        raise
    finally:
        db.close()
    logger.info(f"YouTube ingestion completed for {region}")


if __name__ == "__main__":
    ingest("US")
    ingest("IN")
