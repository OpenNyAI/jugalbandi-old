# JB Auth Token

This package takes care of authorization token management. It does the auth token operations like encoding or creating access and refresh tokens, decoding access and refresh tokens, etc.

The methods and classes provided by this package are:

- **TokenData** : a class that provides a type of token response that contains username with string datatype.
- **create_access_token** : a method to create access token which takes in the username for the encoding process
- **create_refresh_token** : a method to create refresh token which takes in the username for the encoding process
- **decode_token** : a method to decode access token which takes in the access token for the decoding process
- **decode_refresh_token** : a method to decode refresh token which takes in the refresh token for the decoding process

While using this package in any service, some environment variables need to be declared in the `.env` file of the service:

- **TOKEN_ACCESS_TOKEN_EXPIRE_MINUTES** (the period of time the access token will remain valid, default value : 60)
- **TOKEN_REFRESH_TOKEN_EXPIRE_MINUTES** (the period of time the refresh token will remain valid, default value : 60 _ 24 _ 7)
- **TOKEN_ALGORITHM** (algorithm used to encode and decode the tokens, default value : HS256)
- **TOKEN_JWT_SECRET_KEY** (the secret key used to encode and decode the access token)
- **TOKEN_JWT_SECRET_REFRESH_KEY** (the secret key used to encode and decode the refresh token)

# 🔧 1. Installation

To use the code, you need to follow these steps:

1. Clone the repository from GitHub:

   ```bash
   git clone git@github.com:OpenNyAI/jugalbandi.git
   ```

2. The code requires **Python 3.7 or higher** and the project follows poetry package system. If poetry is already installed, skip this step. To install [poetry](https://python-poetry.org/docs/), run the following command in your terminal:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Once poetry is installed, go into the **jb-auth-token** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the token classes and methods from this package by running the **token.py** file or export this package to other services to use the token methods and classes.
