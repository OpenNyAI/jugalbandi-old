import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List

from jugalbandi.audio_converter import convert_to_wav_with_ffmpeg
from jugalbandi.core.errors import IncorrectInputException
from jugalbandi.core.language import Language
from jugalbandi.core.media_format import MediaFormat
from jugalbandi.document_collection import DocumentCollection
from jugalbandi.logging import Logger
from jugalbandi.speech_processor import SpeechProcessor
from jugalbandi.translator import Translator
from pydantic import BaseModel

from .query_with_gptindex import querying_with_gptindex
from .query_with_langchain import querying_with_langchain

logger = Logger("qa_engine")


class QueryResponse(BaseModel):
    query: str
    query_in_english: str = ""
    answer: str
    answer_in_english: str = ""
    audio_output_url: str = ""
    source_text: List[Any] = []


class LangchainQAModel(Enum):
    GPT35_TURBO = "gpt-3.5-turbo-1106"
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
        translator: Translator,
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
                    self.document_collection, query
                )
            if output_format.name == "VOICE":
                is_voice = True

        else:
            wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
            query = await self.speech_processor.speech_to_text(wav_data, input_language)
            is_voice = True

        if answer == "":
            query_in_english = await self.translator.translate_text(
                query, input_language, Language.EN
            )
            answer, source_text = await querying_with_gptindex(
                self.document_collection, query_in_english
            )
            answer_in_english = await self.translator.translate_text(
                answer, Language.EN, input_language
            )

        if is_voice:
            audio_content = await self.speech_processor.text_to_speech(
                answer, input_language
            )
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "output_audio_files/audio-output-" + time_stamp + ".mp3"
            await self.document_collection.write_audio_file(filename, audio_content)
            audio_output_url = await self.document_collection.audio_file_public_url(
                filename
            )

        return QueryResponse(
            query=query,
            query_in_english=query_in_english,
            answer=answer,
            answer_in_english=answer_in_english,
            audio_output_url=audio_output_url,
            source_text=source_text,
        )


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

    async def query(
        self,
        query: str = "",
        speech_query_url: str = "",
        prompt: str = "",
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        is_voice = False
        answer = ""
        answer_in_english = ""
        query_in_english = ""
        audio_output_url = ""
        if query == "" and speech_query_url == "":
            error_message = "Query input is missing"
            logger.error(error_message)
            raise IncorrectInputException(error_message)

        if query != "":
            logger.info("Query Type: Text")
            if output_format.name == "VOICE":
                logger.info("Response Type: Voice")
                is_voice = True
            else:
                logger.info("Response Type: Text")
        else:
            logger.info("Query Type: Voice")
            wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
            logger.info("Audio converted to wav")
            query = await self.speech_processor.speech_to_text(wav_data, input_language)
            logger.info("Response Type: Voice")
            is_voice = True

        logger.info(f"User Query: {query}")
        logger.info("Query Input Language: " + input_language.value)
        query_in_english = await self.translator.translate_text(
            query, input_language, Language.EN
        )
        answer_in_english = await querying_with_langchain(
            self.document_collection, query_in_english, prompt, self.model.value
        )
        answer = await self.translator.translate_text(
            answer_in_english, Language.EN, input_language
        )
        logger.info("RAG is successful")
        logger.info(f"Query in English: {query_in_english}")
        # logger.info(f"K value: {str(k)}")
        # logger.info(f"Chunks: {', '.join(chunks)}")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Answer in English: {answer_in_english}")
        logger.info(f"Answer: {answer}")

        if is_voice:
            audio_content = await self.speech_processor.text_to_speech(
                answer, input_language
            )
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "output_audio_files/audio-output-" + time_stamp + ".mp3"
            logger.info(f"Writing audio file: {filename}")
            await self.document_collection.write_audio_file(filename, audio_content)
            audio_output_url = await self.document_collection.audio_file_public_url(
                filename
            )
            logger.info(f"Audio output URL: {audio_output_url}")

        logger.info("RAG Engine process completed successfully")
        return QueryResponse(
            query=query,
            query_in_english=query_in_english,
            answer=answer,
            answer_in_english=answer_in_english,
            audio_output_url=audio_output_url,
        )
