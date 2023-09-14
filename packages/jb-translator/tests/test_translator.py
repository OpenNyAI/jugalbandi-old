import pytest
import os
from jugalbandi.translator.translator import DhruvaTranslator, GoogleTranslator
from jugalbandi.core.language import Language
from dotenv import load_dotenv

load_dotenv()
test_dir = os.path.dirname(__file__)


@pytest.fixture(scope="session", autouse=True)
def dhruvaTranslator():
    return DhruvaTranslator()


@pytest.fixture(scope="session", autouse=True)
def googleTranslator():
    return GoogleTranslator()


@pytest.mark.asyncio
async def test_dhruva_translator(dhruvaTranslator: DhruvaTranslator):
    file_path = os.path.join(test_dir, "test_mockups/test_text.txt")
    with open(file_path) as f:
        query = f.readlines()
    english_text = await dhruvaTranslator.translate_text(
        textQuery=query[0],
        source_language=Language.HI,
        destination_language=Language.EN,
    )
    assert (
        english_text
        == "Who is a civil servant according to the Karnataka State Civil Services Act?"
    )


@pytest.mark.asyncio
async def test_google_translator(googleTranslator: GoogleTranslator):
    file_path = os.path.join(test_dir, "test_mockups/test_text.txt")
    with open(file_path) as f:
        query = f.readlines()
    english_text = await googleTranslator.translate_text(
        text=query[0],
        source_language=Language.HI,
        destination_language=Language.EN,
    )
    assert (
        english_text
        == "Who is a civil servant as per Karnataka State Civil Services Act"
    )
