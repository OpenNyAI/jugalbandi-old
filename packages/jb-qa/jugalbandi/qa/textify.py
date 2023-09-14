import re
from jugalbandi.document_collection import DocumentCollection, DocumentFormat
import fitz
import docx2txt


def docx_to_text_converter(docx_file_path):
    text = docx2txt.process(docx_file_path)
    return text


def pdf_to_text_converter(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    content = "\n"
    for page in doc:
        text = page.get_text("text", textpage=None, sort=False)
        text = re.sub(r'\n\d+\s*\n', '\n', text)
        content += text
    return content


class TextConverter:
    async def textify(self, filename: str, doc_collection: DocumentCollection) -> str:
        file_path = doc_collection.local_file_path(filename)
        if filename.endswith(".pdf"):
            content = pdf_to_text_converter(file_path)
        elif filename.endswith(".docx"):
            content = docx_to_text_converter(file_path)
        else:
            with open(file_path, "r") as f:
                content = f.read()

        # remove multiple new lines between paras
        regex = r"(?<!\n\s)\n(?!\n| \n)"
        content = re.sub(regex, "", content)

        content = repr(content)[1:-1]
        await doc_collection.write_file(filename, content, DocumentFormat.TEXT)
        await doc_collection.public_url(filename, DocumentFormat.TEXT)
        return content
