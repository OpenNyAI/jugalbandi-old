from io import BytesIO
import httpx
import re
import json
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse
from jiva.db import JivaRepository
from .model import (
    DocumentInfo,
    DocumentsList,
    QueryResult,
    DocumentResponseItem,
    SectionResponseItem,
    ConversationHistory,
    OpenedDocuments,
    FeedbackUpdateRequest,
    Bookmark,
    BookmarkUpdate,
)
from .helper import (
  get_jiva_repo,
  verify_access_token,
  get_library,
  get_translator
)
from .model import User
from fastapi.middleware.cors import CORSMiddleware
from jugalbandi.library import DocumentMetaData
from jugalbandi.legal_library.legal_library import LegalLibrary, ActMetaData
from jugalbandi.translator import Translator
from jugalbandi.core.language import Language
from PIL import Image
from typing import Dict, List
from datetime import datetime
import fitz

user_app = FastAPI()

user_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@user_app.exception_handler(Exception)
async def custom_exception_handler(request, exception):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error_message": str(exception)}
    )


@user_app.get(
    "/query",
    response_model=QueryResult,
    operation_id="query",
    tags=["Query"],
)
async def query(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    translator: Annotated[Translator, Depends(get_translator)],
    query: str,
    language: Language,
):
    if language != Language.EN:
        query = await translator.translate_text(query, language, Language.EN)
    pattern = re.compile(r"\b[Ss]ec(?:tion)?", re.IGNORECASE)
    matches = re.search(pattern, query)
    if matches:
        responses = await jiva_library.search_sections(query)
        section_response = [
            SectionResponseItem(section=response) for response in responses
        ]
        return QueryResult(items=section_response)  # type: ignore
    else:
        responses = await jiva_library.search_titles(query)
        document_response = [
            DocumentResponseItem(metadata=response) for response in responses
        ]
        return QueryResult(items=document_response)  # type: ignore


@user_app.get(
    "/document/{document_id}",
)
async def get_document(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    document_id: str,
    page_number: Optional[str] = None,
) -> Response:
    catalog = await jiva_library.catalog()
    document = catalog[document_id]
    pdf_url = document.public_url
    response = httpx.get(pdf_url)
    buffer = BytesIO(response.content)

    if page_number is not None:
        page_no = int(page_number)
        pdf_document = fitz.open(stream=buffer.read(), filetype="pdf")
        if page_no < 1 or page_no > pdf_document.page_count:
            raise ValueError("Invalid page number")

        page = pdf_document.load_page(page_no - 1)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")
        image_buffer.seek(0)
        return Response(content=image_buffer.read(), media_type="image/png")
    else:
        return Response(content=buffer.read(), media_type="application/pdf")


@user_app.get(
    "/documents",
    response_model=DocumentsList,
    operation_id="get_documents",
    tags=["Document List"],
)
async def get_documents(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    language: Language,
):
    catalog = await jiva_library.catalog()
    documents = [DocumentInfo(id=cat, title=catalog[cat].title) for cat in catalog]
    return DocumentsList(documents=documents)


@user_app.get(
    "/document-info/{document_id}",
    response_model=DocumentMetaData,
    operation_id="get_document_info",
    tags=["Document"],
)
async def get_document_info(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    translator: Annotated[Translator, Depends(get_translator)],
    document_id: str,
):
    document = jiva_library.get_document(document_id)
    return await document.read_metadata()


@user_app.get(
    "/document-section-info/{document_id}",
    operation_id="get_document_section_info",
    tags=["Document"],
)
async def get_document_sections_info(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    translator: Annotated[Translator, Depends(get_translator)],
    document_id: str,
):
    document = jiva_library.get_document(document_id)
    byte_sections = await document.read_sections()
    sections = json.loads(byte_sections.decode("utf-8"))
    return sections


@user_app.get(
    "/act-info/{act_id}",
    response_model=ActMetaData,
    operation_id="get_act_info",
    tags=["Act"],
)
async def get_act_info(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_library: Annotated[LegalLibrary, Depends(get_library)],
    translator: Annotated[Translator, Depends(get_translator)],
    act_id: str,
):
    act_catalog = await jiva_library.act_catalog()
    acts = act_catalog.values()
    for act in acts:
        if act.id == act_id:
            return act


@user_app.get(
    "/daily-activities/{email_id}",
    tags=["Conversation History"],
)
async def get_daily_activities(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
):
    daily_activities: Dict[str, List] = {}
    conversation_list = await jiva_repository.get_daily_activities(email_id=email_id)
    for conversation in conversation_list:
        message_id = str(conversation.get("message_id"))
        message_date = str(conversation.get("message_date"))
        message_time = str(conversation.get("message_time").strftime('%H:%M'))
        query = conversation.get("query")
        if message_date not in daily_activities:
            daily_activities[message_date] = []

        daily_activities[message_date].append(
            {
                "message_id": message_id,
                "activity": "Searched",
                "title": query,
                "time": message_time
                }
        )

    list_of_activities = []
    for activity in daily_activities:
        activity_date = datetime.strptime(activity, "%Y-%m-%d")
        formatted_activity_date = activity_date.strftime("%B %d, %Y")
        activity_obj = {
            "date": formatted_activity_date,
            "activities": daily_activities[activity]
        }
        list_of_activities.append(activity_obj)

    return JSONResponse(
        content={
            "daily_activities": list_of_activities
        },
        status_code=200,
    )


@user_app.delete(
    "/daily-activities/{email_id}/{message_id}",
    tags=["Conversation History"],
)
async def delete_daily_activity(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
    message_id: str
):
    await jiva_repository.delete_activity(email_id=email_id, message_id=message_id)
    return JSONResponse(
        content={"response": "Activity deleted successfully"}, status_code=200
    )


@user_app.get(
    "/conversation-history/{email_id}",
    tags=["Conversation History"],
)
async def get_conversation_history(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
):
    conversation_history_list = await jiva_repository.get_conversation_history(
        email_id=email_id
    )
    return conversation_history_list


@user_app.put(
    "/conversation-history",
    tags=["Conversation History"],
)
async def put_conversation_history(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    feedback_update_request: FeedbackUpdateRequest,
):
    await jiva_repository.put_feedback_into_conversation(
        email_id=feedback_update_request.email_id,
        message_id=feedback_update_request.message_id,
        feedback=feedback_update_request.feedback,
    )


@user_app.put(
    "/bookmark",
    tags=["BookMark"]
)
async def update_bookmark(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    bookmark_update_request: BookmarkUpdate
):
    await jiva_repository.update_bookmark(
        email_id=bookmark_update_request.email_id,
        bookmark_id=bookmark_update_request.bookmark_id,
        document_id=bookmark_update_request.document_id,
        document_title=bookmark_update_request.document_title,
        section_name=bookmark_update_request.section_name,
        bookmark_name=bookmark_update_request.bookmark_name,
        bookmark_note=bookmark_update_request.bookmark_note,
        bookmark_page=bookmark_update_request.bookmark_page
    )

    return JSONResponse(
        content={
            "response": "Bookmark updated successfully",
        },
        status_code=200,
    )


@user_app.post(
    "/conversation-history",
    tags=["Conversation History"],
)
async def post_conversation_history(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    conversation_history: ConversationHistory,
):
    message_id = await jiva_repository.insert_conversation_history(
        email_id=conversation_history.email_id,
        query=conversation_history.query,
        message=conversation_history.message,
        sender=conversation_history.sender,
        feedback=conversation_history.feedback,
    )
    return JSONResponse(
        content={
            "response": "Conversation is inserted successfully",
            "chat_message_id": str(message_id),
        },
        status_code=200,
    )


@user_app.delete(
    "/conversation-history/{email_id}",
    tags=["Conversation History"],
)
async def delete_conversation_history(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
):
    await jiva_repository.delete_conversation_history(email_id=email_id)
    return JSONResponse(
        content={"response": "Conversation is cleared successfully"}, status_code=200
    )


@user_app.delete(
    "/bookmarks/{email_id}/{bookmark_id}",
    tags=["BookMark"],
)
async def delete_bookmark(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
    bookmark_id: str
):
    await jiva_repository.delete_bookmark(email_id=email_id, bookmark_id=bookmark_id)
    return JSONResponse(
        content={"response": "Bookmark is deleted successfully"}, status_code=200
    )


@user_app.get(
        "/bookmarks/{email_id}",
        tags=["BookMark"],
)
async def get_bookmarks(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
):
    bookmark_list = await jiva_repository.get_bookmarks(
        email_id=email_id
    )
    return bookmark_list


@user_app.post(
    "/bookmarks",
    tags=["BookMark"],
)
async def post_bookmark(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    bookmark: Bookmark,
):
    bookmark_id = await jiva_repository.insert_bookmark(
        email_id=bookmark.email_id,
        document_id=bookmark.document_id,
        document_title=bookmark.document_title,
        section_name=bookmark.section_name,
        bookmark_name=bookmark.bookmark_name,
        bookmark_note=bookmark.bookmark_note,
        bookmark_page=bookmark.bookmark_page,
    )
    print(bookmark_id)
    return JSONResponse(
        content={
            "response": "bookmark is inserted successfully",
            "bookmark_id": str(bookmark_id),
        },
        status_code=200,
    )


@user_app.get(
    "/opened-documents/{email_id}",
    response_model=List[OpenedDocuments],
    tags=["Opened Documents"],
)
async def get_opened_documents(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
):
    opened_documents = await jiva_repository.get_opened_documents(email_id=email_id)
    return opened_documents


@user_app.post(
    "/opened-documents",
    tags=["Opened Documents"],
)
async def post_opened_documents(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    opened_documents: OpenedDocuments,
):
    await jiva_repository.insert_opened_documents(
        email_id=opened_documents.email_id,
        document_title=opened_documents.document_title,
        document_id=opened_documents.document_id,
    )
    return JSONResponse(
        content={"response": "Opened documents are inserted successfully"},
        status_code=200,
    )


@user_app.delete(
    "/opened-documents/{email_id}",
    tags=["Opened Documents"],
)
async def delete_opened_documents(
    authorization: Annotated[User, Depends(verify_access_token)],
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    email_id: str,
    document_id: str,
):
    await jiva_repository.delete_opened_documents(
        email_id=email_id, document_id=document_id
    )
    return JSONResponse(
        content={"response": "Opened documents are cleared successfully"},
        status_code=200,
    )


@user_app.post("/query-response-feedback", include_in_schema=False)
async def post_query_response_feedback(
    jiva_repository: Annotated[JivaRepository, Depends(get_jiva_repo)],
    translator: Annotated[Translator, Depends(get_translator)],
    query: str,
    document_title: str,
    feedback: bool,
    section_name: str = "",
    section_page_number: str = "",
):
    await jiva_repository.insert_query_response_feedback(
        query=query,
        document_title=document_title,
        section_name=section_name,
        section_page_number=section_page_number,
        feedback=feedback,
    )
    return JSONResponse(
        content={"detail": "Feedback update is successful"}, status_code=200
    )
