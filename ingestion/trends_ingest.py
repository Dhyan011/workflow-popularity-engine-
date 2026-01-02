import time
import random
from pytrends.request import TrendReq
from backend.app.logger import logger


from backend.app.db.database import SessionLocal
from backend.app.models.workflow import Workflow

pytrends = TrendReq(hl="en-US", tz=360)

KEYWORDS = [
    "n8n workflow",
    "n8n automation",
    "n8n google sheets",
    "n8n slack",
    "n8n whatsapp",
    "n8n ai agent",
]


def ingest(country: str):
    logger.info(f"\nStarting Google Trends ingestion for {country}")
    try:
        db = SessionLocal()
        for keyword in KEYWORDS:

            pytrends.build_payload(
                [keyword],
                timeframe="today 90-d",
                geo=country,
            )

            data = pytrends.interest_over_time()

            if data.empty:
                logger.info(f"No trend data for {keyword}")
                continue

            avg_interest = int(data[keyword].mean())
            peak_interest = int(data[keyword].max())
            momentum = int(data[keyword].iloc[-7:].mean())

            existing = (
                db.query(Workflow)
                .filter(
                    Workflow.platform == "google",
                    Workflow.source_id == keyword,
                    Workflow.country == country,
                )
                .first()
            )

            if existing:
                existing.views = avg_interest
                existing.likes = peak_interest
                existing.comments = momentum
                logger.info(f"Updated trend: {keyword}")
            else:
                db.add(
                    Workflow(
                        workflow_name=keyword,
                        platform="google",
                        source_id=keyword,
                        country=country,
                        views=avg_interest,
                        likes=peak_interest,
                        comments=momentum,
                        like_to_view_ratio=0,
                        comment_to_view_ratio=0,
                    )
                )
                logger.info(f"Inserted trend: {keyword}")

            db.commit()

            # critical: avoid 429
            time.sleep(random.uniform(5, 9))

            # rate limiting
            logger.warning(f"Skipped {keyword} due to rate limit", exc_info=True)
            time.sleep(15)
    except Exception:
        logger.error("Failed to make Google Trends ingestion")
        db.rollback()
        raise
    finally:
        db.close()
        logger.info(f"Google Trends ingestion completed for {country}")


if __name__ == "__main__":
    ingest("US")
    ingest("IN")
