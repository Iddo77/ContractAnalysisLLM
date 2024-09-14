# backend/models.py

from pydantic import BaseModel
from typing import List, Optional


class ContractUploadResponse(BaseModel):
    message: str
    contract_filename: str


class TaskUploadResponse(BaseModel):
    message: str
    tasks_uploaded: int


class TaskAnalysisRequest(BaseModel):
    task_descriptions: List[str]
    task_costs: List[float]


class TaskAnalysisResult(BaseModel):
    task_description: str
    task_cost: float
    compliance: bool
    reasons: List[str]
    ambiguity: bool
    applicable_terms: List[str]


class TaskAnalysisResponse(BaseModel):
    results: List[TaskAnalysisResult]
