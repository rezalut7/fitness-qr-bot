from sqlmodel import SQLModel, Field
from datetime import datetime

class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tg_id: int
    full_name: str
    phone: str
    consent_at: datetime
    registered_at: datetime = Field(default_factory=datetime.utcnow)
