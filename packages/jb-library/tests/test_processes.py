import logging
import os
from jugalbandi.library.pipeline import LocalDocument
from jugalbandi.library.sections import SectionPdf, SectionReview


async def test_section():
    dirname = os.path.dirname(__file__)
    local_doc = LocalDocument(f"{dirname}/sample_doc", "abcd.pdf")
    action = SectionPdf()
    await action.execute(local_doc)
    action2 = SectionReview()
    status = await action2.execute(local_doc)
    logging.info(status)
    status2 = await action2.execute(local_doc)
    logging.info(status2)
    await local_doc.write_task_response("section_review", bytes("hello", "utf-8"))
    status3 = await action2.execute(local_doc)
    logging.info(status3)
