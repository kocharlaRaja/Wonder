from pydantic import BaseModel
from datetime import datetime

class CalculationBase(BaseModel):
    expression: str

class CalculationCreate(CalculationBase):
    pass

class CalculationResponse(CalculationBase):
    id: int
    timestamp: datetime
    result: str

    class Config:
        orm_mode = True
