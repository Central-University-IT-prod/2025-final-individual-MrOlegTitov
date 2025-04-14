from pydantic import BaseModel


class Time(BaseModel):
    current_date: int
