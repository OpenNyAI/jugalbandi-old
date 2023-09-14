import csv
from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, validator
import aiofiles
from jugalbandi.library import DocumentMetaData, DocumentFormat
from jugalbandi.legal_library import (
    LegalLibrary,
    LegalDocumentType,
    Jurisdiction,
    LegalKeys,
)


anpr_date_format_str = "%d-%m-%Y %H:%M:%S.%f"
fastag_date_format_str = "%Y-%m-%d %H:%M:%S.%f"


def parse_timestamp(timestamp_str: str, is_fastag: bool) -> datetime:
    date_format = fastag_date_format_str if is_fastag else anpr_date_format_str
    substr = timestamp_str[0:21]
    return datetime.strptime(substr, date_format)


class LibraryImport(BaseModel):
    file_name: str
    publish_date: Optional[date]
    type: LegalDocumentType
    doc_title: str
    pass_date: Optional[date]
    effective_from: Optional[date]
    jurisdiction: Jurisdiction
    ministry: Optional[str] = None
    related_act_title: Optional[str] = None
    related_act_no: str

    class Config:
        json_decoders = {date: lambda v: datetime.strptime(v, "%d-%m-%Y").date()}
        use_enum_values = True

    @validator("publish_date", "pass_date", "effective_from", pre=True)
    @classmethod
    def validate_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%m-%Y").date()


def read_library_folder(lib_folder: str = "lib") -> List[LibraryImport]:
    # Add
    docs: List[LibraryImport] = []
    import_file_name = f"{lib_folder}/index.csv"
    with open(import_file_name) as f:
        reader = csv.DictReader(f)
        try:
            for row in reader:
                obj = LibraryImport.parse_obj(row)
                docs.append(obj)
        except csv.Error as e:
            print(f"file {import_file_name}, line {reader.line_num}: {e}")
        except Exception as e:
            print(f"file {import_file_name}, line {reader.line_num}: {e}")

    return docs


async def import_act_docs(legal_library: LegalLibrary, lib_folder: str = "lib"):
    lib_entries = read_library_folder(lib_folder)

    for lib_entry in lib_entries:
        extra_data: Dict[str, str] = {}
        extra_data[LegalKeys.LEGAL_DOC_TYPE] = lib_entry.type
        extra_data[LegalKeys.LEGAL_ACT_JURISDICTION] = lib_entry.jurisdiction
        extra_data[LegalKeys.LEGAL_ACT_NO] = lib_entry.related_act_no

        if lib_entry.related_act_title is not None:
            extra_data[LegalKeys.LEGAL_ACT_TITLE] = lib_entry.related_act_title

        if lib_entry.ministry is not None:
            extra_data[LegalKeys.LEGAL_MINISTRY] = lib_entry.ministry

        if lib_entry.pass_date is not None:
            extra_data[LegalKeys.LEGAL_PASS_DATE] = lib_entry.pass_date.strftime(
                "%Y-%m-%d"
            )
        if lib_entry.effective_from is not None:
            extra_data[
                LegalKeys.LEGAL_EFFECTIVE_DATE
            ] = lib_entry.effective_from.strftime("%Y-%m-%d")

        md = DocumentMetaData(
            title=lib_entry.doc_title,
            original_file_name=lib_entry.file_name,
            original_format=DocumentFormat.PDF,
            publish_date=lib_entry.publish_date,
            extra_data=extra_data,
        )

        filepath = f"{lib_folder}/{lib_entry.file_name}"
        async with aiofiles.open(filepath, "rb") as f:
            content = await f.read()

        await legal_library.add_document(md, content)
