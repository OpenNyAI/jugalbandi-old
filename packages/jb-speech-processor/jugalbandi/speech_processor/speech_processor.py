import base64
import httpx
import os
from jugalbandi.core import (
    Language,
    InternalServerException,
)
from jugalbandi.audio_converter.converter import convert_wav_bytes_to_mp3_bytes
from google.cloud import texttospeech, speech
from abc import ABC, abstractmethod
import json


class SpeechProcessor(ABC):
    @abstractmethod
    async def speech_to_text(self, wav_data: bytes, input_language: Language) -> str:
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, input_language: Language) -> bytes:
        pass


class DhruvaSpeechProcessor(SpeechProcessor):
    def __init__(self):
        self.bhashini_user_id = os.getenv('BHASHINI_USER_ID')
        self.bhashini_api_key = os.getenv('BHASHINI_API_KEY')
        self.bhashini_pipleline_id = os.getenv('BHASHINI_PIPELINE_ID')
        self.bhashini_inference_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    async def perform_bhashini_config_call(self,
                                           task: str,
                                           source_language: str,
                                           target_language: str | None = None):
        url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        if task in ['asr', 'tts']:
            payload = json.dumps({
                "pipelineTasks": [
                    {
                        "taskType": task,
                        "config": {
                            "language": {
                                "sourceLanguage": source_language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            })
        else:
            payload = json.dumps({
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language,
                                "targetLanguage": target_language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": self.bhashini_pipleline_id
                }
            })
        headers = {
            'userID': self.bhashini_user_id,
            'ulcaApiKey': self.bhashini_api_key,
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=payload)  # type: ignore

        return response.json()

    async def speech_to_text(self, wav_data: bytes, input_language: Language) -> str:
        bhashini_asr_config = await self.perform_bhashini_config_call(
            task='asr', source_language=input_language.name.lower())
        encoded_string = base64.b64encode(wav_data).decode("ascii", "ignore")

        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": bhashini_asr_config['languages'][0]['sourceLanguage'],
                        },
                        "serviceId": bhashini_asr_config['pipelineResponseConfig'][0]['config'][0]['serviceId'],
                        "audioFormat": "wav",
                        "samplingRate": 16000
                    }
                }
            ],
            "inputData": {
                "audio": [
                    {
                        "audioContent": encoded_string}
                ]
            }
        })
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
            bhashini_asr_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
                bhashini_asr_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value'],
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=self.bhashini_inference_url,
                                         headers=headers,
                                         data=payload)  # type: ignore
        if response.status_code != 200:
            raise InternalServerException(
                f"Request failed with response.text: {response.text} and "
                  f"status_code: {response.status_code}")

        return response.json()['pipelineResponse'][0]['output'][0]['source']

    async def text_to_speech(self,
                             text: str,
                             input_language: Language,
                             gender='female') -> bytes:
        bhashini_tts_config = await self.perform_bhashini_config_call(
            task='tts', source_language=input_language.name.lower())

        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": bhashini_tts_config['languages'][0]['sourceLanguage']
                        },
                        "serviceId": bhashini_tts_config['pipelineResponseConfig'][0]['config'][0]['serviceId'],
                        "gender": gender,
                        "samplingRate": 8000
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text
                    }
                ]
            }
        })
        headers = {
            'Accept': '*/*',
            'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
            bhashini_tts_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
                bhashini_tts_config['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value'],
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url=self.bhashini_inference_url,
                                         headers=headers,
                                         data=payload)  # type: ignore
        if response.status_code != 200:
            raise InternalServerException(
                f"Request failed with response.text: {response.text} and "
                  f"status_code: {response.status_code}")

        audio_content = response.json()['pipelineResponse'][0]['audio'][0]['audioContent']
        audio_content = base64.b64decode(audio_content)
        new_audio_content = convert_wav_bytes_to_mp3_bytes(audio_content)
        return new_audio_content


class GoogleSpeechProcessor(SpeechProcessor):
    def __init__(self):
        self.language_dict = {
            "EN" : "en-US",
            "HI" : "hi-IN",
            "BN" : "bn-IN",
            "GU" : "gu-IN",
            "MR" : "mr-IN",
            "OR" : "or-IN",
            "PA" : "pa-IN",
            "KN" : "kn-IN",
            "ML" : "ml-IN",
            "TA" : "ta-IN",
            "TE" : "te-IN",
            "AF" : "af-ZA",
            "AR" : ["ar-DZ", "ar-XA"],
            "ZH" : "yue-HK",
            "FR" : "fr-FR",
            "DE" : "de-DE",
            "ID" : "id-ID",
            "IT" : "it-IT",
            "JA" : "ja-JP",
            "KO" : "ko-KR",
            "PT" : "pt-PT",
            "RU" : "ru-RU",
            "ES" : "es-ES",
            "TR" : "tr-TR"
        }

    async def speech_to_text(self, wav_data: bytes, input_language: Language) -> str:
        language_code = self.language_dict[input_language.name]
        if isinstance(language_code, list):
            language_code = language_code[0]
        client = speech.SpeechAsyncClient()
        audio = speech.RecognitionAudio(content=wav_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
        )
        response = await client.recognize(config=config, audio=audio)
        return response.results[0].alternatives[0].transcript

    async def text_to_speech(self, text: str, input_language: Language) -> bytes:
        language_code = self.language_dict[input_language.name]
        if isinstance(language_code, list):
            language_code = language_code[1]
        client = texttospeech.TextToSpeechAsyncClient()
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = await client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        audio_content = response.audio_content
        return audio_content


class CompositeSpeechProcessor(SpeechProcessor):
    def __init__(self, *speech_processors: SpeechProcessor):
        self.speech_processors = speech_processors
        self.european_language_codes = ["EN", "AF", "AR", "ZH", "FR", "DE", "ID",
                                        "IT", "JA", "KO", "PT", "RU", "ES", "TR"]

    async def speech_to_text(self, wav_data: bytes, input_language: Language) -> str:
        excs = []
        for speech_processor in self.speech_processors:
            try:
                if (input_language.name in self.european_language_codes and
                        isinstance(speech_processor, DhruvaSpeechProcessor)):
                    pass
                else:
                    return await speech_processor.speech_to_text(wav_data, input_language)
            except Exception as exc:
                excs.append(exc)

        raise ExceptionGroup("CompositeSpeechProcessor speech to text failed", excs)

    async def text_to_speech(self, text: str, input_language: Language) -> bytes:
        excs = []
        for speech_processor in self.speech_processors:
            try:
                if (input_language.name in self.european_language_codes and
                        isinstance(speech_processor, DhruvaSpeechProcessor)):
                    pass
                else:
                    return await speech_processor.text_to_speech(text, input_language)
            except Exception as exc:
                excs.append(exc)

        raise ExceptionGroup("CompositeSpeechProcessor text to speech failed", excs)
