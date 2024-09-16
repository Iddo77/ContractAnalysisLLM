# backend/models.py

from pydantic import BaseModel
from typing import List, Optional, Dict


class ContractUploadResponse(BaseModel):
    message: str
    contract_filename: str
    contract_json: str


class TaskUploadResponse(BaseModel):
    message: str
    tasks_uploaded: int


class Term(BaseModel):
    title: str
    content: str


class TaskAnalysisResult(BaseModel):
    task_description: str
    task_cost: float
    applicable_terms: List[Term]
    reasoning: str
    compliance: bool
    ambiguous: bool


class TaskAnalysisResponse(BaseModel):
    results: List[TaskAnalysisResult]


class Section(BaseModel):
    title: str
    terms: List[Term]
    subsections: List['Section'] = []


class Contract(BaseModel):
    title: str
    definitions: Dict[str, str]
    sections: List[Section]
