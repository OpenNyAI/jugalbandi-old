from fastapi.testclient import TestClient
from labeling.api import app
from labeling.model import User
from labeling.helper import verify_access_token
import pytest

client = TestClient(app)


@pytest.fixture(scope="module")
def override_get_user():
    def get_mock_user():
        return User(name="Tester", email="tester@gmail.com")

    app.dependency_overrides[verify_access_token] = get_mock_user
    yield

    app.dependency_overrides.pop(verify_access_token)


@pytest.mark.asyncio
async def test_get_cases():
    try:
        response = client.get("/cases")
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 105
    except Exception as e:
        pytest.fail(f"Testing failed due to {e}")


@pytest.mark.asyncio
async def test_get_cases_with_authentication(override_get_user):
    try:
        response = client.get("/cases")
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 1
    except Exception as e:
        pytest.fail(f"Testing failed due to {e}")


@pytest.mark.asyncio
async def test_get_case_with_case_id():
    try:
        response = client.get("/cases/86759466")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json['case_name'] == "M/S.Doshi Motors Pvt. Ltd vs The Commercial Tax Officer, ... on 27 August, 2014"
    except Exception as e:
        pytest.fail(f"Testing failed due to {e}")


@pytest.mark.asyncio
async def test_generate_issues_with_case_id():
    try:
        response = client.get("/generate-issues?case_id=86759466")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json != ""
    except Exception as e:
        pytest.fail(f"Testing failed due to {e}")


@pytest.mark.asyncio
async def test_generate_arguments_with_case_id():
    try:
        response = client.get("/generate-arguments?case_id=86759466&generate_arguments_for=petitioners")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json != ""
    except Exception as e:
        pytest.fail(f"Testing failed due to {e}")
