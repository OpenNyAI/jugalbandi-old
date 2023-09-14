from fastapi.testclient import TestClient
from generic_qa.server import app
from generic_qa.server_middleware import ApiKeyMiddleware
from jugalbandi.core.errors import UnAuthorisedException, QuotaExceededException
import pytest
import os

test_dir = os.path.dirname(__file__)
client = TestClient(app)


class MockDBRepository:
    async def get_balance_quota_from_api_key(self):
        pass

    async def update_balance_quota(self):
        pass


@pytest.fixture
def test_client():
    middleware = ApiKeyMiddleware(app=app, tenant_repository=MockDBRepository())
    app.user_middleware.clear()
    app.dependency_overrides[ApiKeyMiddleware] = lambda: middleware
    app.middleware_stack = app.build_middleware_stack()
    test_client = TestClient(app)
    return test_client


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Jugalbandi API"}


def test_upload_files(test_client, monkeypatch):
    monkeypatch.setenv("GCP_BUCKET_FOLDER_NAME", "testing/doc_repo")
    monkeypatch.setenv("DOCUMENT_LOCAL_STORAGE_PATH", "tests/local")
    file_path = os.path.join(test_dir, "test_mockups/indexing/testing.pdf")
    if os.path.exists(file_path):
        file = open(file_path, "rb")
        try:
            response = test_client.post(
                "/upload-files?api_key=dummy_key",
                files={"files": ("testing.pdf", file, "application/pdf")},
            )
            response_json = response.json()
            assert response.status_code == 200
            assert response_json["message"] == "Files uploading is successful"
        except Exception as e:
            pytest.fail(f"Uploading failed due to {e}")
    else:
        pytest.fail("Test file does not exist.")


def test_upload_zip_file(test_client, monkeypatch):
    monkeypatch.setenv("GCP_BUCKET_FOLDER_NAME", "testing/doc_repo")
    monkeypatch.setenv("DOCUMENT_LOCAL_STORAGE_PATH", "tests/local")
    file_path = os.path.join(test_dir, "test_mockups/indexing/Archive.zip")
    if os.path.exists(file_path):
        file = open(file_path, "rb")
        try:
            response = test_client.post(
                "/upload-files?api_key=dummy_key",
                files={"files": ("Archive.zip", file, "application/zip")},
            )
            response_json = response.json()
            assert response.status_code == 200
            assert response_json["message"] == "Files uploading is successful"
        except Exception as e:
            pytest.fail(f"Uploading failed due to {e}")
    else:
        pytest.fail("Test file does not exist.")


def test_query_with_gpt_index(test_client):
    uuid_number = "a959a476-fdef-11ed-a270-3e85235234ab"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-with-gptindex?uuid_number={uuid_number}&query_string={query}"
                "&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["answer"] != ""
            and len(response_json["source_text"]) > 0
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_with_langchain(test_client):
    uuid_number = "7fc2fd6c-ab63-11ed-80d8-3e85235234ac"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-with-langchain?uuid_number={uuid_number}&query_string={query}"
                "&api_key=dummy_key"),
        )
        response_json = response.json()
        print(response_json)
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["answer"] != ""
            and len(response_json["source_text"]) > 0
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_rephrased_query(test_client):
    query_string = "Give me section 14 of IPC"
    try:
        response = test_client.get(
            f"/rephrased-query?query_string={query_string}&api_key=dummy_key",
        )
        response_json = response.json()
        print(response_json)
        assert response.status_code == 200
        assert (
            response_json["given_query"] == query_string
            and response_json["rephrased_query"]
            == "What is the content of section 14 of the Indian Penal Code?"
        )
    except Exception as e:
        pytest.fail(f"Rephrasing query failed due to {e}")


def test_query_with_langchain_gpt3_5(test_client):
    uuid_number = "bb01d73a-ea52-11ed-9bb7-378d76577400"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-with-langchain-gpt3-5?uuid_number={uuid_number}"
                f"&query_string={query}&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["answer"] != ""
            and len(response_json["source_text"]) > 0
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_with_langchain_gpt3_5_and_custom_prompt(test_client):
    uuid_number = "84470664-09d0-11ee-ab56-3e85235234ab"
    query = "Give me definition of civil servant"
    prompt = ("You are a helpful assistant who helps with answering questions based "
              "on the provided information. Do not answer out of context questions.")
    try:
        response = test_client.get(
            (f"/query-with-langchain-gpt3-5-custom-prompt?uuid_number={uuid_number}"
                f"&query_string={query}&prompt={prompt}&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["answer"] != ""
            and len(response_json["source_text"]) == 0
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_with_langchain_gpt4(test_client):
    uuid_number = "a959a476-fdef-11ed-a270-3e85235234ab"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-with-langchain-gpt4?uuid_number={uuid_number}"
                f"&query_string={query}&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["query"] == query and response_json["answer"] != ""
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_with_langchain_gpt4_and_custom_prompt(test_client):
    uuid_number = "84470664-09d0-11ee-ab56-3e85235234ab"
    query = "Who is Michael Jackson"
    prompt = ("You are a helpful assistant who helps with answering questions based "
              "on the provided information. Do not answer out of context questions.")
    try:
        response = test_client.get(
            (f"query-with-langchain-gpt4-custom-prompt?uuid_number={uuid_number}"
                f"&query_string={query}&prompt={prompt}&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["query"] == query and response_json["answer"] != ""
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_using_voice_input(test_client):
    uuid_number = "7fc2fd6c-ab63-11ed-80d8-3e85235234ac"
    input_language = "English"
    output_format = "Voice"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-using-voice?uuid_number={uuid_number}&query_text={query}"
                f"&input_language={input_language}&output_format={output_format}"
                "&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["query_in_english"] is not None
            and response_json["answer"] != ""
            and response_json["answer_in_english"] is not None
            and response_json["audio_output_url"] != ""
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


def test_query_using_voice_input_gpt4(test_client):
    uuid_number = "a959a476-fdef-11ed-a270-3e85235234ab"
    input_language = "English"
    output_format = "Voice"
    query = "Give me definition of civil servant"
    try:
        response = test_client.get(
            (f"/query-using-voice-gpt4?uuid_number={uuid_number}&query_text={query}"
                f"&input_language={input_language}&output_format={output_format}"
                "&api_key=dummy_key"),
        )
        response_json = response.json()
        assert response.status_code == 200
        assert (
            response_json["query"] == query
            and response_json["query_in_english"] is not None
            and response_json["answer"] != ""
            and response_json["answer_in_english"] is not None
            and response_json["audio_output_url"] != ""
        )
    except Exception as e:
        pytest.fail(f"Querying failed due to {e}")


# Will fail because of the invalid key rerouting to default key
def test_rephrased_query_endpoint_with_invalid_key():
    with pytest.raises(UnAuthorisedException):
        response = client.get("/rephrased-query?query_string=hello&api_key=invalid_key")
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid API key"}


def test_rephrased_query_endpoint_with_exhausted_quota():
    exhausted_key = "ab81c16a43063a003eabb606beeb9f83"
    with pytest.raises(QuotaExceededException):
        response = client.get(f"/rephrased-query?query_string=hello&api_key={exhausted_key}")
        assert response.status_code == 429
        assert response.json() == {"detail": "You have exceeded the quota limit"}


def test_rephrased_query_endpoint_with_invalid_key_routing_to_default_key():
    response = client.get("/rephrased-query?query_string=hello&api_key=dummy_key")
    assert response.status_code == 200
