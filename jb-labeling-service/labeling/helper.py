from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jugalbandi.core.caching import aiocached
from jugalbandi.auth_token.token import decode_token, decode_refresh_token
from .db import LabelingRepository
from .model import User, TokenLength
from typing import Annotated
import os
import openai
import time
import tiktoken


@aiocached(cache={})
async def get_labeling_repo() -> LabelingRepository:
    labeling_repo = LabelingRepository()
    return labeling_repo


reusable_oauth = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def verify_access_token(labeling_repo: Annotated[LabelingRepository, Depends(get_labeling_repo)],
                              token: Annotated[str, Depends(reusable_oauth)]):
    if os.environ["ALLOW_AUTH_ACCESS"] == "true" and token is None:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_details = await labeling_repo.get_user(email=username)
    return User(name=user_details.get("name"),
                email=user_details.get("email"),
                affliation=user_details.get("affliation"))


async def verify_refresh_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_refresh_token(token)
        username: str = payload
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username


async def call_openai_api(messages, max_tokens=1024, model='gpt-3.5-turbo'):
    retry_cnt = 0
    retry_limit = 3
    openai.api_key = os.environ["OPENAI_API_KEY"]
    while retry_cnt < retry_limit:
        try:
            completions = openai.ChatCompletion.create(model=model,
                                                       messages=messages,
                                                       max_tokens=max_tokens,
                                                       n=1,
                                                       stop=None,
                                                       temperature=0)
            return completions.choices[0].message.content
        except Exception:
            retry_cnt += 1
            time.sleep(1)


async def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613") -> int:
    # Return the number of tokens used by a list of messages.
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # If there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return await num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return await num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>
    return num_tokens


async def choose_openai_model_based_on_length(messages, max_output_len):
    # Returns which openai model should be used based on the length. Returns None if too long
    input_token_cnt = await num_tokens_from_messages(messages, model='gpt-4')
    argument_generation_context_length = input_token_cnt + max_output_len
    if argument_generation_context_length <= TokenLength.MAX_GPT4.value:
        model = 'gpt-4'
    elif argument_generation_context_length <= TokenLength.MAX_GPT3_5_TURBO.value:
        model = 'gpt-3.5-turbo'
    else:
        model = None
    return model
