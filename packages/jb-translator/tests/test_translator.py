import pytest
import os
from jugalbandi.translator.translator import DhruvaTranslator, GoogleTranslator, AzureTranslator
from jugalbandi.core.language import Language
from dotenv import load_dotenv

load_dotenv()
test_dir = os.path.dirname(__file__)


@pytest.fixture(scope="session", autouse=True)
def dhruva_translator():
    return DhruvaTranslator()


@pytest.fixture(scope="session", autouse=True)
def azure_translator():
    return AzureTranslator()


@pytest.fixture(scope="session", autouse=True)
def google_translator():
    return GoogleTranslator()


@pytest.mark.asyncio
async def test_dhruva_translator(dhruva_translator: DhruvaTranslator):
    file_path = os.path.join(test_dir, "test_mockups/hindi_text.txt")
    with open(file_path) as f:
        query = f.readlines()
    english_text = await dhruva_translator.translate_text(
        text=query[0],
        source_language=Language.HI,
        destination_language=Language.EN,
    )
    assert (
        english_text
        == "Who is a civil servant according to the Karnataka State Civil Services Act?"
    )


@pytest.mark.asyncio
async def test_azure_translator(azure_translator: AzureTranslator):
    file_path = os.path.join(test_dir, "test_mockups/hindi_text.txt")
    with open(file_path) as f:
        query = f.readlines()
    english_text = await azure_translator.translate_text(
        text=query[0],
        source_language=Language.HI,
        destination_language=Language.EN,
    )
    assert (
        english_text
        == "Who is a Civil Servant as per Karnataka State Civil Services Act"
    )


@pytest.mark.asyncio
async def test_google_translator(google_translator: GoogleTranslator):
    file_path = os.path.join(test_dir, "test_mockups/hindi_text.txt")
    with open(file_path) as f:
        query = f.readlines()
    english_text = await google_translator.translate_text(
        text=query[0],
        source_language=Language.HI,
        destination_language=Language.EN,
    )
    assert (
        english_text
        == "Who is a civil servant as per Karnataka State Civil Services Act"
    )
