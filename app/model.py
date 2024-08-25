from pydantic import BaseModel
from typing import List

class SampleRequest(BaseModel):
    samples: List[float]