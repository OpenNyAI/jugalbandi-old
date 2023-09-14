import pytest
import os
from jugalbandi.audio_converter.converter import (
    convert_to_wav,
    convert_to_wav_with_ffmpeg,
)

test_dir = os.path.dirname(__file__)
TEST_FILE_PATH = "https://storage.googleapis.com/jugalbandi"


def test_audio_conversion_of_mp3_file():
    file_path = os.path.join(test_dir, "test_mockups/hindi_audio.mp3")
    if os.path.isfile(file_path):
        wav_data = convert_to_wav(file_path)
        assert wav_data is not None and type(wav_data) == bytes
    else:
        pytest.fail("Test file does not exist.")


@pytest.mark.asyncio
async def test_audio_conversion_of_ogg_file():
    file_path = os.path.join(test_dir, "test_mockups/english_audio.ogg")
    if os.path.isfile(file_path):
        wav_data = await convert_to_wav_with_ffmpeg(file_path)
        assert wav_data is not None and type(wav_data) == bytes
    else:
        pytest.fail("Test file does not exist.")


def test_audio_conversion_of_file_url():
    file_url = f"{TEST_FILE_PATH}/generic_qa/music_files/new_hindi_audio.mp3"
    wav_data = convert_to_wav(file_url)
    assert wav_data is not None and type(wav_data) == bytes


@pytest.mark.asyncio
async def test_audio_conversion_of_file_url_with_ffmpeg():
    file_url = f"{TEST_FILE_PATH}/generic_qa/music_files/english_voice.mp3"
    wav_data = await convert_to_wav_with_ffmpeg(file_url)
    assert wav_data is not None and type(wav_data) == bytes
