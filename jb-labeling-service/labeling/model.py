from typing import List
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class CaseSection(BaseModel):
    section_number: str
    act_title: str
    reason: str
    description: str
    is_applicable: bool


class CasePrecedent(BaseModel):
    precedent_name: str
    precedent_url: str
    paragraphs: List[str]


class Case(BaseModel):
    case_id: str
    case_name: str
    case_type: str
    court_name: str
    court_type: str
    doc_url: str
    raw_text: str
    doc_size: int
    facts: str
    facts_edited: bool = False
    facts_last_updated_at: List[datetime] = []
    facts_cumulative_time: int = 0
    facts_reviewed: bool = False
    issues: List[str] = []
    issues_edited: bool = False
    issues_last_updated_at: List[datetime] = []
    issues_cumulative_time: int = 0
    issues_reviewed: bool = False
    generated_issues: str = ""
    sections: List[CaseSection] = []
    sections_edited: bool = False
    sections_last_updated_at: List[datetime] = []
    sections_cumulative_time: int = 0
    sections_reviewed: bool = False
    precedents: List[CasePrecedent] = []
    precedents_edited: bool = False
    precedents_last_updated_at: List[datetime] = []
    precedents_cumulative_time: int = 0
    precedents_reviewed: bool = False
    petitioner_arguments: List[str] = []
    petitioner_arguments_edited: bool = False
    petitioner_arguments_last_updated_at: List[datetime] = []
    petitioner_arguments_cumulative_time: int = 0
    petitioner_arguments_reviewed: bool = False
    generated_petitioner_arguments: str = ""
    respondent_arguments: List[str] = []
    respondent_arguments_edited: bool = False
    respondent_arguments_last_updated_at: List[datetime] = []
    respondent_arguments_cumulative_time: int = 0
    respondent_arguments_reviewed: bool = False
    generated_respondent_arguments: str = ""
    is_completed: bool = False
    petitioner_name: str = ""
    respondent_name: str = ""


class User(BaseModel):
    name: str
    email: str
    affliation: str | None = None
    password: str | None = None


class TokenLength(Enum):
    MAX_FACTS = 10000
    MAX_ISSUES = 3000
    MAX_CUMULATIVE = 14000
    MAX_GENERATED_ISSUE = 1024
    MAX_GENERATED_ARGUMENTS = 2048
    MAX_GPT4 = 8192
    MAX_GPT3_5_TURBO = 16384
