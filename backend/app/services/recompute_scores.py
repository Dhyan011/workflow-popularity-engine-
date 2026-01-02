from backend.app.db.database import SessionLocal
from backend.app.services.scoring import recompute_all_scores
from backend.app.logger import logger


def main():
    db = SessionLocal()
    try:
        recompute_all_scores(db)
    except Exception:
        logger.error("Failed to recompute all scores", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
