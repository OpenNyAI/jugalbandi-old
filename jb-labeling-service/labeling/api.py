from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from .db import LabelingRepository
from .model import (
    Case,
    CasePrecedent,
    CaseSection,
    User,
    TokenLength
)
from .helper import (
    verify_access_token,
    get_labeling_repo
)
from .argument_generation import (
    generate_issues,
    generate_arguments
)
from .auth_api import auth_app
from dotenv import load_dotenv
import tiktoken

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Autocomplete to get all case details
@app.get(
        "/cases",
        tags=["Case"])
async def get_cases(
    authorization: Annotated[User, Depends(verify_access_token)],
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)]
):
    if authorization:
        user_email = authorization.email
    else:
        user_email = None
    cases = await labeling_repo.get_cases_from_user_email(user_email=user_email)
    case_list = []
    for case in cases:
        case_list.append({
            "case_id": case.get("id"),
            "case_name": case.get("case_name")
        })
    return case_list


# Particular case details
@app.get(
    "/cases/{case_id}",
    response_model=Case,
    operation_id="get_case",
    tags=["Case"],
)
async def get_case(
    authorization: Annotated[User, Depends(verify_access_token)],
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
    case_id: str
):
    print('In here got it')
    case = await labeling_repo.get_case_from_case_id(case_id=case_id)
    sections = await labeling_repo.get_sections_from_case_id(case_id=case_id)
    precedents = await labeling_repo.get_precedents_from_case_id(case_id=case_id)
    section_list = []
    precedent_list = []
    for section in sections:
        section_list.append(CaseSection(section_number=section.get("section_number"),
                                        act_title=section.get("act_title"),
                                        reason=section.get("reason"),
                                        description=section.get("description"),
                                        is_applicable=section.get("is_applicable")))
    for precedent in precedents:
        precedent_list.append(CasePrecedent(precedent_name=precedent.get("precedent_name"),
                                            precedent_url=precedent.get("precedent_url"),
                                            paragraphs=precedent.get("paragraphs")))
    return Case(case_id=case.get("id"),
                case_name=case.get("case_name"),
                case_type=case.get("case_type"),
                court_name=case.get("court_name"),
                court_type=case.get("court_type"),
                doc_url=case.get("doc_url"),
                raw_text=case.get("raw_text"),
                doc_size=case.get("doc_size"),
                facts=case.get("facts"),
                facts_edited=case.get("facts_edited"),
                facts_last_updated_at=case.get("facts_last_updated_at"),
                facts_cumulative_time=case.get("facts_cumulative_time"),
                facts_reviewed=case.get("facts_reviewed"),
                issues=case.get("issues"),
                issues_edited=case.get("issues_edited"),
                issues_last_updated_at=case.get("issues_last_updated_at"),
                issues_cumulative_time=case.get("issues_cumulative_time"),
                issues_reviewed=case.get("issues_reviewed"),
                generated_issues=case.get("generated_issues"),
                sections=section_list,
                sections_edited=case.get("sections_edited"),
                sections_last_updated_at=case.get("sections_last_updated_at"),
                sections_cumulative_time=case.get("sections_cumulative_time"),
                sections_reviewed=case.get("sections_reviewed"),
                precedents=precedent_list,
                precedents_edited=case.get("precedents_edited"),
                precedents_last_updated_at=case.get("precedents_last_updated_at"),
                precedents_cumulative_time=case.get("precedents_cumulative_time"),
                precedents_reviewed=case.get("precedents_reviewed"),
                petitioner_arguments=case.get("petitioner_arguments"),
                petitioner_arguments_edited=case.get("petitioner_arguments_edited"),
                petitioner_arguments_last_updated_at=case.get("petitioner_arguments_last_updated_at"),
                petitioner_arguments_cumulative_time=case.get("petitioner_arguments_cumulative_time"),
                petitioner_arguments_reviewed=case.get("petitioner_arguments_reviewed"),
                generated_petitioner_arguments=case.get("generated_petitioner_arguments"),
                respondent_arguments=case.get("respondent_arguments"),
                respondent_arguments_edited=case.get("respondent_arguments_edited"),
                respondent_arguments_last_updated_at=case.get("respondent_arguments_last_updated_at"),
                respondent_arguments_cumulative_time=case.get("respondent_arguments_cumulative_time"),
                respondent_arguments_reviewed=case.get("respondent_arguments_reviewed"),
                generated_respondent_arguments=case.get("generated_respondent_arguments"),
                petitioner_name=case.get("petitioner_name"),
                respondent_name=case.get("respondent_name"))


# Facts update
@app.post(
    "/cases/{case_id}/facts",
    operation_id="update_case_facts",
    tags=["Case"],
)
async def update_case_facts(authorization: Annotated[User, Depends(verify_access_token)],
                            labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                            case_id: str,
                            case: Case):
    encoding = tiktoken.get_encoding("cl100k_base")
    facts_token_length = len(encoding.encode(case.facts))

    if facts_token_length < TokenLength.MAX_FACTS.value:
        await labeling_repo.update_case_facts(case_id=case_id,
                                              case=case,
                                              facts_token_length=facts_token_length)
    else:
        raise HTTPException(status_code=422,
                            detail=f"Facts should be less than 10,000 tokens. Current tokens are {facts_token_length}")


# Issues update
@app.post(
    "/cases/{case_id}/issues",
    operation_id="update_case_issues",
    tags=["Case"],
)
async def update_case_issues(authorization: Annotated[User, Depends(verify_access_token)],
                             labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                             case_id: str,
                             case: Case):
    encoding = tiktoken.get_encoding("cl100k_base")
    issues_token_length = 0
    for issue in case.issues:
        issues_token_length += len(encoding.encode(issue))

    if issues_token_length < TokenLength.MAX_ISSUES.value:
        await labeling_repo.update_case_issues(case_id=case_id,
                                               case=case,
                                               issues_token_length=issues_token_length)
    else:
        raise HTTPException(status_code=422,
                            detail=f"Issues should be less than 3000 tokens. Current tokens are {issues_token_length}")


# Sections update
@app.post(
    "/cases/{case_id}/sections",
    operation_id="update_case_sections",
    tags=["Case"],
)
async def update_case_sections(authorization: Annotated[User, Depends(verify_access_token)],
                               labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                               case_id: str,
                               case: Case):
    await labeling_repo.update_case_sections(case_id=case_id, case=case)


# Precedents update
@app.post(
    "/cases/{case_id}/precedents",
    operation_id="update_case_precedents",
    tags=["Case"],
)
async def update_case_precedents(authorization: Annotated[User, Depends(verify_access_token)],
                                 labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                                 case_id: str,
                                 case: Case):
    encoding = tiktoken.get_encoding("cl100k_base")
    cumulative_token_length = await labeling_repo.get_token_length_from_case_id(case_id=case_id)
    for section in case.sections:
        section_string = "Section " + section.section_number + " of " + section.act_title
        cumulative_token_length += len(encoding.encode(section_string))

    for precedent in case.precedents:
        precedent_string = 'Source: ' + precedent.precedent_name + '\nparagraphs: ' + " ".join(precedent.paragraphs)
        cumulative_token_length += len(encoding.encode(precedent_string))

    if cumulative_token_length < TokenLength.MAX_CUMULATIVE.value:
        await labeling_repo.update_case_precedents(case_id=case_id,
                                                   case=case,
                                                   cumulative_token_length=cumulative_token_length)
    else:
        raise HTTPException(status_code=422,
                            detail=f"Please reduce the precedents size. Current token size is {cumulative_token_length}")


# Arguments update
@app.post(
    "/cases/{case_id}/arguments",
    operation_id="update_case_arguments",
    tags=["Case"],
)
async def update_case_arguments(authorization: Annotated[User, Depends(verify_access_token)],
                                labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                                case_id: str,
                                case: Case) -> bool:
    await labeling_repo.update_case_arguments(case_id=case_id, case=case)
    return await labeling_repo.is_given_case_completed(case_id=case_id)


# Generate issues
@app.get(
    "/generate-issues",
    operation_id="get_generated_issues",
    tags=["Case"],
)
async def generate_issues_from_case_id(
    authorization: Annotated[User, Depends(verify_access_token)],
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
    case_id: str
) -> str:
    case = await labeling_repo.get_case_from_case_id(case_id=case_id)
    facts = case.get("facts")
    generated_issues = await generate_issues(facts=facts)
    return generated_issues


# Generate arguments
@app.get(
    "/generate-arguments",
    operation_id="get_generated_arguments",
    tags=["Case"],
)
async def generate_arguments_from_case_id(
    authorization: Annotated[User, Depends(verify_access_token)],
    labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
    case_id: str,
    generate_arguments_for: str,
    other_party_arguments: str = ""
) -> str:
    case = await labeling_repo.get_case_from_case_id(case_id=case_id)
    sections = await labeling_repo.get_sections_from_case_id(case_id=case_id)
    precedents = await labeling_repo.get_precedents_from_case_id(case_id=case_id)
    facts = case.get("facts")
    issues_list = case.get("issues")
    court_name = case.get("court_name")
    petitioner_name = case.get("petitioner_name")
    respondent_name = case.get("respondent_name")
    issues = " ".join(issues_list)
    statues_list = []
    for section in sections:
        if section.get("is_applicable"):
            statues_list.append("Section " + section.get("section_number") + " of " + section.get("act_title"))

    precedent_paras = []
    for precedent in precedents:
        precedent_paras.append({
            "source": precedent.get("precedent_name"),
            "para_text": " ".join(precedent.get("paragraphs"))})

    generated_arguments = await generate_arguments(court_name=court_name,
                                                   petitioner_name=petitioner_name,
                                                   respondent_name=respondent_name,
                                                   facts=facts,
                                                   statutes_list=statues_list,
                                                   issues=issues,
                                                   generate_arguments_for=generate_arguments_for,
                                                   precedent_paras=precedent_paras,
                                                   other_party_arguments=other_party_arguments)
    return generated_arguments


app.mount("/auth", auth_app)
