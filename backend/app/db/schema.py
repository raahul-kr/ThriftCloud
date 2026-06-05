from sqlalchemy import inspect, text

from app.db.models import Base
from app.db.session import engine


def ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "recommendation_records" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("recommendation_records")}
    additions = {
        "assigned_owner": "VARCHAR(255)",
        "acknowledged_at": "DATETIME",
    }

    with engine.begin() as connection:
        for column_name, column_type in additions.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(f"ALTER TABLE recommendation_records ADD COLUMN {column_name} {column_type}")
            )
