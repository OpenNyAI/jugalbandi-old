import pytest
import os
from jugalbandi.audio_converter import convert_to_wav_with_ffmpeg
from jugalbandi.speech_processor import (
    DhruvaSpeechProcessor,
    GoogleSpeechProcessor,
    AzureSpeechProcessor,
    CompositeSpeechProcessor,
)
from jugalbandi.core.language import Language
from dotenv import load_dotenv

load_dotenv()
test_dir = os.path.dirname(__file__)


@pytest.fixture()
def dhruva_speech_processor():
    return DhruvaSpeechProcessor()


@pytest.fixture()
def azure_speech_processor():
    return AzureSpeechProcessor()


@pytest.fixture()
def google_speech_processor():
    return GoogleSpeechProcessor()


@pytest.fixture()
def composite_speech_processor():
    return CompositeSpeechProcessor(DhruvaSpeechProcessor(), GoogleSpeechProcessor())


@pytest.mark.asyncio
async def test_dhruva_speech_to_text(dhruva_speech_processor: DhruvaSpeechProcessor):
    file_path = os.path.join(test_dir, "test_mockups/hindi_audio.mp3")
    if os.path.isfile(file_path):
        wav_data = await convert_to_wav_with_ffmpeg(file_path)
        text_data = await dhruva_speech_processor.speech_to_text(
            wav_data, Language.HI
        )
        assert (
            text_data is not None
            and text_data
            == "कर्नाटक राज्य नागरिक सेवा अधिनियम के अनुसार एक सिविल सेवक कौन है"
        )
    else:
        pytest.fail("Test file does not exist.")


@pytest.mark.asyncio
async def test_dhruva_text_to_speech(dhruva_speech_processor: DhruvaSpeechProcessor):
    audio_bytes = await dhruva_speech_processor.text_to_speech(
        "कर्नाटक राज्य नागरिक सेवा अधिनियम के अनुसार एक सिविल सेवक कौन है",
        Language.HI,
    )
    assert audio_bytes is not None and isinstance(audio_bytes, bytes)


@pytest.mark.asyncio
async def test_azure_speech_to_text(azure_speech_processor: AzureSpeechProcessor):
    file_path = os.path.join(test_dir, "test_mockups/tamil_audio.mp3")
    if os.path.isfile(file_path):
        wav_data = await convert_to_wav_with_ffmpeg(file_path)
        text_data = await azure_speech_processor.speech_to_text(
            wav_data, Language.TA
        )
        assert (
            text_data is not None
            and text_data
            == "கர்நாடக மாநில சிவில் சர்வீஸ் சட்டத்தின்படி அரசு ஊழியர் யார்?"
        )
    else:
        pytest.fail("Test file does not exist.")


@pytest.mark.asyncio
async def test_azure_text_to_speech(azure_speech_processor: AzureSpeechProcessor):
    audio_bytes = await azure_speech_processor.text_to_speech(
        "கர்நாடக மாநில சிவில் சர்வீசஸ் சட்டத்தின்படி அரசு ஊழியர் யார்?",
        Language.TA,
    )
    assert audio_bytes is not None and isinstance(audio_bytes, bytes)


@pytest.mark.asyncio
async def test_google_speech_to_text(google_speech_processor: GoogleSpeechProcessor):
    file_path = os.path.join(test_dir, "test_mockups/hindi_audio.mp3")
    if os.path.isfile(file_path):
        wav_data = await convert_to_wav_with_ffmpeg(file_path)
        text_data = await google_speech_processor.speech_to_text(wav_data, Language.HI)
        assert (
            text_data is not None
            and text_data
            == "कर्नाटक राज्य नागरिक सेवा अधिनियम के अनुसार एक सिविल सेवक कौन है"
        )
    else:
        pytest.fail("Test file does not exist.")


@pytest.mark.asyncio
async def test_google_text_to_speech(google_speech_processor: GoogleSpeechProcessor):
    audio_bytes = await google_speech_processor.text_to_speech(
        "कर्नाटक राज्य नागरिक सेवा अधिनियम के अनुसार एक सिविल सेवक कौन है",
        Language.HI,
    )
    assert audio_bytes is not None and isinstance(audio_bytes, bytes)


@pytest.mark.asyncio
async def test_composite_speech_to_text(composite_speech_processor: CompositeSpeechProcessor):
    file_path = os.path.join(test_dir, "test_mockups/english_audio.mp3")
    if os.path.isfile(file_path):
        wav_data = await convert_to_wav_with_ffmpeg(file_path)
        text_data = await composite_speech_processor.speech_to_text(
            wav_data, Language.EN
        )
        assert text_data is not None and text_data == (
            "Who is the civil servant according to"
            " Karnataka State Civil Services Act?"
        )
    else:
        pytest.fail("Test file does not exist.")


@pytest.mark.asyncio
async def test_composite_text_to_speech(composite_speech_processor: CompositeSpeechProcessor):
    audio_bytes = await composite_speech_processor.text_to_speech(
        "who is the civil servant according to karnataka state civil services act",
        Language.EN,
    )
    assert audio_bytes is not None and isinstance(audio_bytes, bytes)
