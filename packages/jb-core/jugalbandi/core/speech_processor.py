from enum import Enum


class SpeechProcessor(str, Enum):
    AZURE = "Azure"
    GOOGLE = "Google"
    DHRUVA = "Dhruva"
