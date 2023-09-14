# Auth Service : Plug-n-Play Authentication Service

The [Auth service](https://api.jugalbandi.ai/auth/docs) acts like a plug-n-play service in a way such that it can be plugged into any service which needs authentication mechanism. It uses basic login and signup endpoints to validate authentication, using OAuth methods.

While using this service in any other services, some environment variables need to be declared in the `.env` file of the service, that uses it:

- AUTH_DATABASE_IP
- AUTH_DATABASE_PORT
- AUTH_DATABASE_USERNAME
- AUTH_DATABASE_PASSWORD
- AUTH_DATABASE_NAME

# 🔧 1. Installation

To use the code, you need to follow these steps:

1. Clone the repository from GitHub:

   ```bash
   git clone git@github.com:OpenNyAI/jugalbandi.git
   ```

2. The code requires **Python 3.7 or higher** and the project follows poetry package system. To install [poetry](https://python-poetry.org/docs/), run the following command in your terminal:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Once poetry is installed, go into the **jb-auth-service** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

4. This service uses other packages such as jb-auth-token, jb-core. Hence their respective environment variables may also be required. Please refer to their respective repositories for more information.

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in jb-auth-service folder of the repository in terminal

```bash
poetry run poe start
```

You can then access the APIs and their specification in [http://localhost:8080/library/auth/docs](http://localhost:8080/library/auth/docs)

# 📃 3. API Specification and Documentation

### `POST /signup`

Registers a particular user, with username and password, in the database

#### Request

Requires at least username and password, for successful registration.

#### Successful Response

```json
{}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, it is checked whether the username already exists in the database. If username does not exist in the database, the password is encrypted and then it is inserted into the database along with the username, thus forming a new record and a blank JSON is returned with status code 200. If the username already exists in the database, then it returns an error message "User with this email already exist" along with status code 422.

---

### `POST /login`

#### Request

Authenticates an user by its registered username and password and creates access and refresh tokens for the user.

#### Successful Response

```json
{
  "access_token": "<your-access-token>",
  "token_type": "bearer",
  "refresh_token": "<your-refresh-token>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, it is checked whether the username exists in the database. If not, an error message "Incorrect email" is returned, along with status code 422; but if it exists, the user record is returned and the encrypted password for that particular username is obtained from the record. Then verification of password happens between the password that has come as part of the request, and the encrpted password from the database. If verification is successful, it returns response containing access token and refresh token; else, it returns an error message "Incorrect password" with status code 422.

---

# 📜🖋 5. Poetry commands

- All the poetry commands like install, run, build, test, etc. are wrapped inside a script called **poe**. You can check out and customize the commands in **pyproject.toml** file.
- Adding package through poetry:

  - To add a new python package to the project, run the following command:

    ```bash
    poetry add <package-name>
    ```

  - To add a custom package to the project, run the following command:

    ```bash
    poetry add <path_to_custom_package> --editable
    ```

- Removing package through poetry:

  - To remove a python package from the project, run the following command:

    ```bash
    poetry remove <package-name>
    ```

- Running tests through poetry:

  - To run all the tests, run the following command:

    ```bash
    poetry run poe test
    ```

  - To run a specific test, run the following command:

    ```bash
    poetry run poe test <path_to_test_file>
    ```

# 👩‍💻 6. Usage

To directly use the Jugalbandi Auth APIs without cloning the repo, you can follow below steps to get you started:

1.  Visit [https://api.jugalbandi.ai/auth/docs](https://api.jugalbandi.ai/auth/docs).
2.  Go to the `/signup` endpoint to create a new user.
3.  Once you have created a new user, you should have received a `{}` for that username. Please keep the username and password handy as it will be required for you to login.
4.  Now that you have the username and password as a new user you can login by the `/login` endpoint and get your access and refresh tokens.
5.  The refresh and access tokens are valid for a certain period of time and you can set the expiry time of the tokens respectively, which is further discussed in `jb-auth-token` package.

## Feature request and contribution

- We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
- Kindly visit our project board to see what is it that we are prioritizing.
