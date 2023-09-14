import fitz
import re
import tempfile
from .library import Document, LibraryFileType


def _karnataka_act_sections(file_path):
    end_string = "and reason"
    pattern = re.compile(re.escape(end_string), re.IGNORECASE)
    doc = fitz.open(file_path)
    content = "\n"
    for i in range(len(doc)):
        flag = False
        page = doc[i]
        text = page.get_text("text", textpage=None, sort=False)
        # text = re.sub(r'\n\d+\s*\n', '\n', text)
        if i == 0:
            occurences = text.lower().count(end_string)
            if occurences == 2:
                text = pattern.split(text)[1]
                flag = True
        else:
            if end_string in text.lower():
                text = pattern.split(text)[0]
                text = pattern.sub(text, "")
                flag = True

        content += text
        if flag is True:
            break

    return content


class SectionPdf:
    @property
    def name(self):
        return "section"

    async def execute(self, doc: Document):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = f"{temp_dir}/local.pdf"
            await doc.read_document(local_file_path=local_file_path)
            content = _karnataka_act_sections(local_file_path)
            await doc.write_sections(bytes(content, "utf-8"))
            await doc.make_public(file_path="section.txt",
                                  file_type=LibraryFileType.SUPPORTING)
