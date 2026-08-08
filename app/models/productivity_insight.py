from pydantic import BaseModel


class ProductivityInsight(BaseModel):
    high_energy_average_error: float
    low_energy_average_error: float