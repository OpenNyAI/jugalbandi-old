import time
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Any
from pydantic import BaseModel
from jugalbandi.document_collection import DocumentCollection
from jugalbandi.speech_processor import SpeechProcessor
from jugalbandi.translator import Translator
from jugalbandi.audio_converter import convert_to_wav_with_ffmpeg
from jugalbandi.core.language import Language
from jugalbandi.core.media_format import MediaFormat
from jugalbandi.core.errors import IncorrectInputException
from .query_with_gptindex import querying_with_gptindex
from .query_with_langchain import (
    querying_with_langchain,
    querying_with_langchain_gpt3_5,
    querying_with_langchain_gpt4
)


class QueryResponse(BaseModel):
    query: str
    query_in_english: str = ""
    answer: str
    answer_in_english: str = ""
    audio_output_url: str = ""
    source_text: List[Any]


class LangchainQAModel(Enum):
    GPT3 = "gpt-3"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT4 = "gpt-4"


class QAEngine(ABC):
    @abstractmethod
    async def query(
        self,
        query: str = "",
        speech_query_url: str = "",
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        pass


class GPTIndexQAEngine:
    def __init__(
        self,
        document_collection: DocumentCollection,
        speech_processor: SpeechProcessor,
        translator: Translator
    ):
        self.document_collection = document_collection
        self.speech_processor = speech_processor
        self.translator = translator

    async def query(
        self,
        query: str = "",
        speech_query_url: str = "",
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        is_voice = False
        answer = ""
        answer_in_english = ""
        query_in_english = ""
        audio_output_url = ""
        source_text = []
        if query == "" and speech_query_url == "":
            raise IncorrectInputException("Query input is missing")

        if query != "":
            if input_language.value == "English":
                answer, source_text = await querying_with_gptindex(
                    self.document_collection, query)
            if output_format.name == "VOICE":
                is_voice = True

        else:
            wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
            query = await self.speech_processor.speech_to_text(wav_data, input_language)
            is_voice = True

        if answer == "":
            query_in_english = await self.translator.translate_text(
                query, input_language, Language.EN)
            answer, source_text = await querying_with_gptindex(
                self.document_collection, query_in_english)
            answer_in_english = await self.translator.translate_text(
                    answer, Language.EN, input_language)

        if is_voice:
            audio_content = await self.speech_processor.text_to_speech(
                answer, input_language)
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "output_audio_files/audio-output-" + time_stamp + ".mp3"
            await self.document_collection.write_audio_file(filename, audio_content)
            audio_output_url = await self.document_collection.audio_file_public_url(
                filename)

        return QueryResponse(query=query, query_in_english=query_in_english,
                             answer=answer,
                             answer_in_english=answer_in_english,
                             audio_output_url=audio_output_url,
                             source_text=source_text)


class LangchainQAEngine:
    def __init__(
        self,
        document_collection: DocumentCollection,
        speech_processor: SpeechProcessor,
        translator: Translator,
        model: LangchainQAModel,
    ):
        self.document_collection = document_collection
        self.speech_processor = speech_processor
        self.translator = translator
        self.model = model
        self.models_dict = {
            LangchainQAModel.GPT3: lambda a, b, c, d, e:
            querying_with_langchain(a, b),
            LangchainQAModel.GPT35_TURBO: lambda a, b, c, d, e:
            querying_with_langchain_gpt3_5(a, b, c, d, e),
            LangchainQAModel.GPT4: lambda a, b, c, d, e:
            querying_with_langchain_gpt4(a, b, c),
        }

    async def query(
        self,
        query: str = "",
        speech_query_url: str = "",
        prompt: str = "",
        source_text_filtering: bool = True,
        model_size: str = "16k",
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        is_voice = False
        answer = ""
        answer_in_english = ""
        query_in_english = ""
        audio_output_url = ""
        source_text = []
        if query == "" and speech_query_url == "":
            raise IncorrectInputException("Query input is missing")

        if query != "":
            if input_language.value == "English":
                answer, source_text = await self.models_dict[self.model](
                    self.document_collection, query, prompt,
                    source_text_filtering, model_size)
            if output_format.name == "VOICE":
                is_voice = True

        else:
            wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
            query = await self.speech_processor.speech_to_text(wav_data, input_language)
            is_voice = True

        if answer == "":
            query_in_english = await self.translator.translate_text(
                query, input_language, Language.EN)
            answer_in_english, source_text = await self.models_dict[self.model](
                self.document_collection, query_in_english, prompt,
                source_text_filtering, model_size)
            answer = await self.translator.translate_text(
                    answer_in_english, Language.EN, input_language)

        if is_voice:
            audio_content = await self.speech_processor.text_to_speech(
                answer, input_language)
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "output_audio_files/audio-output-" + time_stamp + ".mp3"
            await self.document_collection.write_audio_file(filename, audio_content)
            audio_output_url = await self.document_collection.audio_file_public_url(
                filename)

        return QueryResponse(query=query, query_in_english=query_in_english,
                             answer=answer,
                             answer_in_english=answer_in_english,
                             audio_output_url=audio_output_url,
                             source_text=source_text)
