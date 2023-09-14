from typing import Annotated, List, Literal, Union
from pydantic import BaseModel, Field
from jugalbandi.library import DocumentMetaData, DocumentSection


class DocumentResponseItem(BaseModel):
    query_item_type: Literal["document"] = "document"
    metadata: DocumentMetaData


class SectionResponseItem(BaseModel):
    query_item_type: Literal["section"] = "section"
    section: DocumentSection


QueryResponseItem = Annotated[
    Union[DocumentResponseItem, SectionResponseItem],
    Field(discriminator="query_item_type"),
]


class QueryResult(BaseModel):
    items: List[QueryResponseItem]


class DocumentInfo(BaseModel):
    id: str
    title: str


class DocumentsList(BaseModel):
    documents: List[DocumentInfo]


class User(BaseModel):
    name: str
    email_id: str


class SignupRequest(BaseModel):
    name: str
    email_id: str
    password: str


class UpdatePasswordRequest(BaseModel):
    reset_id: int
    verification_code: str
    new_password: str


class FeedbackUpdateRequest(BaseModel):
    email_id: str
    message_id: str
    feedback: bool


class TokenRequest(BaseModel):
    email_id: str
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class ConversationHistory(BaseModel):
    email_id: str
    message: str
    sender: str
    query: str
    feedback: bool | None


class Bookmark(BaseModel):
    email_id: str
    document_id: str
    document_title: str
    section_name: str
    bookmark_name: str
    bookmark_note: str
    bookmark_page: int


class BookmarkUpdate(BaseModel):
    email_id: str
    bookmark_id: str
    document_id: str
    document_title: str
    section_name: str
    bookmark_name: str
    bookmark_note: str
    bookmark_page: int


class OpenedDocuments(BaseModel):
    email_id: str
    document_title: str
    document_id: str
