from jugalbandi.auth_token import (
    create_access_token,
    decode_token,
)


def test_access_token():
    access_token = create_access_token(data={"sub": "sampleuser"})
    decoded_token = decode_token(access_token)
    assert decoded_token == "sampleuser"
