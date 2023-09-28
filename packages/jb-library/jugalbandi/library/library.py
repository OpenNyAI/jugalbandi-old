import asyncio
from enum import Enum
import operator
from typing import Dict, Optional
import uuid
import aiofiles
from pydantic import BaseModel
from datetime import date, datetime
from jugalbandi.storage import Storage
from jugalbandi.core import aiocachedmethod
from cachetools import TTLCache, cachedmethod
import logging


logger = logging.getLogger(__name__)


class DocumentFormat(str, Enum):
    DEFAULT = ""
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "txt"


class DocumentSupportingMetadata(BaseModel):
    doc_id: str
    name: str
    original_file_name: str
    public_url: Optional[str] = None
    create_ts: float = 0.0
    extra_data: Dict[str, str] = {}


class DocumentMetaData(BaseModel):
    id: str = ""
    title: str
    translated_title:  Dict[str, str] = {}
    original_file_name: str
    source: Optional[str] = None
    original_format: DocumentFormat
    create_ts: float = 0.0
    publish_date: Optional[date] = None
    public_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    related_entity: Optional[str] = None
    related_entity_title: Optional[str] = None
    extra_data: Dict[str, str] = {}
    supportings: Dict[str, DocumentSupportingMetadata] = {}

    def get_extra_data(self, field_name: str) -> Optional[str]:
        if field_name in self.extra_data:
            return self.extra_data[field_name]

        return None


class DocumentSection(BaseModel):
    section_id: str
    section_name: str
    start_page: int
    metadata: DocumentMetaData


class Library:
    def __init__(self, id: str, store: Storage):
        self.id = id
        self.store = store
        self._directory_cache: TTLCache = TTLCache(maxsize=2, ttl=900)
        self._task_manager_store_cache: TTLCache = TTLCache(maxsize=2, ttl=900)

    def _file_path(self, file_suffix: str):
        return f"{self.id}/{file_suffix}"

    async def _upload(self, file_path: str, content: bytes):
        await self.store.write_file(file_path, content)

    async def _download(self, file_path: str) -> bytes:
        return await self.store.read_file(file_path)

    async def _make_public(self, file_path: str):
        return await self.store.make_public(file_path)

    @aiocachedmethod(operator.attrgetter("_directory_cache"))
    async def catalog(self):
        cat: Dict[str, DocumentMetaData] = {}

        async def _add_metadata(doc_id):
            document = self.get_document(doc_id)
            metadata = await document.read_metadata()
            cat[doc_id] = metadata

        async with asyncio.TaskGroup() as taskgroup:
            async for doc_id in self.store.list_subfolders(self.id):
                if not doc_id.startswith("__"):
                    taskgroup.create_task(_add_metadata(doc_id))

        return cat

    async def document_exists(self, document_id: str):
        catalog = await self.catalog()
        return document_id in catalog

    async def add_document(self, metadata: DocumentMetaData, content: bytes):
        if metadata.id == "":
            metadata.id = str(uuid.uuid1())
        metadata.create_ts = datetime.now().timestamp()
        document = Document(self, metadata.id)
        await document.write_metadata(metadata)
        await document.write_document(content)
        return document

    async def remove_document(self, document_id: str):
        return await self.store.remove_file(self._file_path(document_id))

    def get_document(self, document_id: str):
        return Document(self, document_id)

    @cachedmethod(operator.attrgetter("_task_manager_store_cache"))
    def get_task_manager_store(self, task_manager_name: str) -> Storage:
        return self.store.new_store(self._file_path(f"__tasks__/{task_manager_name}"))

    async def shutdown(self):
        await self.store.shutdown()


class LibraryFileType(str, Enum):
    DEFAULT = ""
    SECTIONS = "section"
    PIPELINE = "pipeline"
    SUPPORTING = "supporting"
    METADATA = "metadata"
    TASK = "task"


class LibraryFileNameError(Exception):
    pass


class Document:
    def __init__(self, library: Library, doc_id: str):
        self._library = library
        self._id = doc_id
        self._metadata_cache: TTLCache = TTLCache(maxsize=2, ttl=300)

    def _file_path(self, *file_suffix: str) -> str:
        suffix = "/".join(file_suffix)
        return self._library._file_path(f"{self.id}/{suffix}")

    async def _default_file_path(self, format: Optional[DocumentFormat] = None) -> str:
        if format is None or format == DocumentFormat.DEFAULT:
            metadata = await self.read_metadata()
            format = metadata.original_format

        return self._file_path(f"{self.id}.{format.value}")

    async def _file_path_by_type_format(
        self,
        file_path: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        task_name: Optional[str] = None,
        file_type: Optional[LibraryFileType] = LibraryFileType.DEFAULT,
        document_format: Optional[DocumentFormat] = DocumentFormat.DEFAULT,
    ) -> str:
        if file_type == LibraryFileType.DEFAULT:
            if file_path is None:
                return await self._default_file_path(document_format)
            else:
                return self._file_path(file_path)
        if file_type == LibraryFileType.METADATA:
            return self._file_path("metadata.json")
        elif file_type == LibraryFileType.PIPELINE:
            if pipeline_name is not None:
                return self._file_path("__pipeline__", pipeline_name, file_path)
            else:
                raise LibraryFileNameError(
                    f"pipeline_name must be provided for pipeline file {file_path}"
                )
        elif file_type == LibraryFileType.SECTIONS:
            return self._file_path("sections.json")
        elif file_type == LibraryFileType.SUPPORTING:
            return self._file_path("__support__", file_path)
        elif file_type == LibraryFileType.TASK:
            if task_name is not None:
                return self._file_path("__task__", task_name, file_path)
            else:
                raise LibraryFileNameError(
                    f"task_name must be provided for task file {file_path}"
                )
            return self._file_path("__task__", file_path)
        else:
            raise LibraryFileNameError(
                f"Unknown file type for {file_path} - {file_type}"
            )

    async def _write(
        self,
        content: bytes,
        file_path: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        task_name: Optional[str] = None,
        file_type: Optional[LibraryFileType] = LibraryFileType.DEFAULT,
        document_format: Optional[DocumentFormat] = DocumentFormat.DEFAULT,
    ):
        return await self._library._upload(
            await self._file_path_by_type_format(
                file_path=file_path,
                pipeline_name=pipeline_name,
                task_name=task_name,
                file_type=file_type,
                document_format=document_format,
            ),
            content,
        )

    async def _read(
        self,
        file_path: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        task_name: Optional[str] = None,
        file_type: Optional[LibraryFileType] = LibraryFileType.DEFAULT,
        document_format: Optional[DocumentFormat] = DocumentFormat.DEFAULT,
    ):
        return await self._library._download(
            await self._file_path_by_type_format(
                file_path=file_path,
                pipeline_name=pipeline_name,
                task_name=task_name,
                file_type=file_type,
                document_format=document_format,
            )
        )

    @property
    def id(self):
        return self._id

    @property
    def library(self):
        return self._library

    def get_task_manager_store(self, task_manager_name: str):
        return self._library.get_task_manager_store(task_manager_name)

    async def write_metadata(self, metadata: DocumentMetaData):
        await self._write(
            bytes(metadata.json(), "utf-8"),
            file_type=LibraryFileType.METADATA,
        )
        self._metadata_cache.clear()

    @aiocachedmethod(operator.attrgetter("_metadata_cache"))
    async def read_metadata(self) -> DocumentMetaData:
        content = await self._read(file_type=LibraryFileType.METADATA)
        return DocumentMetaData.parse_raw(content)

    async def write_document(
        self,
        content: bytes,
        format: Optional[DocumentFormat] = None,
    ):
        return await self._write(content, document_format=format)

    async def read_document(
        self,
        format: Optional[DocumentFormat] = None,
        local_file_path: Optional[str] = None,
    ):
        content = await self._read(document_format=format)
        if local_file_path is not None:
            async with aiofiles.open(local_file_path, "wb") as f:
                await f.write(content)

    async def write_pipeline_state(self, pipeline_name: str, content: bytes):
        return await self._write(
            content,
            file_path="state.json",
            pipeline_name=pipeline_name,
            file_type=LibraryFileType.PIPELINE,
        )

    async def read_pipeline_state(self, pipeline_name: str) -> Optional[bytes]:
        return await self._read(
            file_path="state.json",
            pipeline_name=pipeline_name,
            file_type=LibraryFileType.PIPELINE,
        )

    async def write_task_file(self, task_name: str, file_path: str, content: bytes):
        return await self._write(
            content,
            file_path=file_path,
            task_name=task_name,
            file_type=LibraryFileType.TASK,
        )

    async def read_task_file(self, task_name: str, file_path: str) -> Optional[bytes]:
        return await self._read(
            file_path=file_path,
            task_name=task_name,
            file_type=LibraryFileType.TASK,
        )

    async def write_supporting_document(
        self,
        supporting_metadata: DocumentSupportingMetadata,
        name: str,
        content: bytes,
    ):
        await self._write(
            content,
            file_path=name,
            file_type=LibraryFileType.SUPPORTING,
        )

        metadata = await self.read_metadata()
        supporting_metadata.create_ts = datetime.now().timestamp()
        metadata.supportings[supporting_metadata.name] = supporting_metadata
        await self.write_metadata(metadata)
        return metadata

    async def read_supporting_document(self, name: str) -> bytes:
        return await self._read(
            file_path=name,
            file_type=LibraryFileType.SUPPORTING,
        )

    async def write_sections(self, content: bytes):
        return await self._write(
            content,
            file_type=LibraryFileType.SECTIONS,
        )

    async def read_sections(self):
        return await self._read(
            file_type=LibraryFileType.SECTIONS,
        )

    async def make_public(
        self,
        file_path: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        task_name: Optional[str] = None,
        file_type: Optional[LibraryFileType] = LibraryFileType.DEFAULT,
        document_format: Optional[DocumentFormat] = DocumentFormat.DEFAULT,
    ) -> str:
        full_file_path = await self._file_path_by_type_format(
            file_path=file_path,
            pipeline_name=pipeline_name,
            task_name=task_name,
            file_type=file_type,
            document_format=document_format,
        )
        logger.info(f"Document: make_public {full_file_path}")
        public_url = await self._library.store.make_public(full_file_path)
        if (
            file_type == LibraryFileType.DEFAULT
            or file_type == LibraryFileType.SUPPORTING
        ):
            metadata = await self.read_metadata()
            if file_type == LibraryFileType.DEFAULT:
                metadata.public_url = public_url
                await self.write_metadata(metadata)
            elif file_path in metadata.supportings:
                metadata.supportings[file_path].public_url = public_url
                if file_path == "thumbnail.png":
                    metadata.thumbnail_url = public_url
                await self.write_metadata(metadata)
            else:
                logger.warn(f"Supporting file not in metadata - {file_path}")

    async def public_url(
        self,
        file_path: Optional[str] = None,
        pipeline_name: Optional[str] = None,
        task_name: Optional[str] = None,
        file_type: Optional[LibraryFileType] = LibraryFileType.DEFAULT,
        document_format: Optional[DocumentFormat] = DocumentFormat.DEFAULT,
    ) -> str:
        full_file_path = await self._file_path_by_type_format(
            file_path=file_path,
            pipeline_name=pipeline_name,
            task_name=task_name,
            file_type=file_type,
            document_format=document_format,
        )
        return await self.library.store.public_url(full_file_path)
