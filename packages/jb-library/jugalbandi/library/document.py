from enum import Enum
import os
from typing import List, Optional, Protocol
import aiofiles
from pathlib import Path
from pydantic import BaseModel
from .library import Library


from .util import path_exists


class DocumentSection(BaseModel):
    no: str
    title: str
    page_no: int = -1


class DocumentSections(BaseModel):
    items: List[DocumentSection]


class DocumentFormat(str, Enum):
    DEFAULT = ""
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "txt"


class Document(Protocol):
    id: str
    library_id: str
    library: Library

    async def read_pipeline_state(self, pipeline_name: str) -> Optional[bytes]:
        pass

    async def write_pipeline_state(self, pipeline_name: str, content: bytes):
        pass

    async def read_document(
        self,
        format: DocumentFormat = DocumentFormat.DEFAULT,
        local_file_path: Optional[str] = None,
    ) -> bytes:
        pass

    async def write_sections(self, content: bytes) -> DocumentSections:
        pass


class LocalDocument(Document):
    def __init__(self, doc_root_folder: str, file_name: str):
        self.doc_root_folder = doc_root_folder
        self.file_name = file_name
        self._file_path = f"{doc_root_folder}/{file_name}"

    async def _write_file(self, file_path: str, content: bytes):
        dirname = os.path.dirname(file_path)
        Path(dirname).mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

    async def _read_file(self, file_path: str) -> bytes:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def read_file(self, local_file_path: Optional[str] = None):
        content = await self._read_file(self._file_path)
        if local_file_path is not None:
            await self._write_file(local_file_path, content)

        return content

    async def read_pipeline_state(self, pipeline_name: str) -> Optional[bytes]:
        if not path_exists(self._file_path):
            return None
        file_path = f"{self.doc_root_folder}/__pipeline__/{pipeline_name}.json"
        return await self._read_file(file_path)

    async def write_pipeline_state(self, pipeline_name: str, content: bytes):
        file_path = f"{self.doc_root_folder}/__pipeline__/{pipeline_name}.json"
        await self._write_file(file_path, content)

    async def write_sections(self, content: bytes):
        file_path = f"{self.doc_root_folder}/sections.json"
        await self._write_file(file_path, content)

    async def task_exists(self, task_name: str):
        file_path = f"{self.doc_root_folder}/__tasks__/{task_name}.json"
        return await path_exists(file_path)

    async def write_task(self, task_name: str, content: bytes):
        file_path = f"{self.doc_root_folder}/__tasks__/{task_name}.json"
        await self._write_file(file_path, content)

    async def write_task_response(self, task_name: str, content: bytes):
        file_path = f"{self.doc_root_folder}/__task_responses__/{task_name}.json"
        await self._write_file(file_path, content)

    async def read_task_response(self, task_name: str) -> Optional[bytes]:
        file_path = f"{self.doc_root_folder}/__task_responses__/{task_name}.json"
        exists = await path_exists(file_path)
        if exists:
            return await self._read_file(file_path)
        else:
            return None
