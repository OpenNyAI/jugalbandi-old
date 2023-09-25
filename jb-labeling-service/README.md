# Labeling Service

Labeling Service is a collection of APIs that are specific to the **Argument Generation application** which provides the necessary endpoints for handling case information and their related data. It uses FastAPI and PostgreSQL to achieve the task at hand.

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

3. Once poetry is installed, go into the **jb-labeling-service** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

```bash
  poetry install
  source .venv/bin/activate
```

4. You will need a GCP account to host a postgres connection to store the case and user details.

5. Create a file named **gcp_credentials.json** which will contain the service account credentials of your GCP account. The file will roughly have the same format mentioned below and can be stored anywhere in your machine.

   ```bash
   {
     "type": "service_account",
     "project_id": "<your-project-id>",
     "private_key_id": "<your-private-key-id>",
     "private_key": "<your-private-key>",
     "client_email": "<your-client-email>",
     "client_id": "<your-client-id>",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x5integer9_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x5integer9_cert_url": "<your-client-cert-url>"
   }
   ```

6. In addition to creating gcp_credentials.json file, create another file **.env** inside the jb-labeling-service folder which will hold the development credentials and add the following variables. Update the openai_api_key and your db connections appropriately.

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   LABELING_DATABASE_NAME=<your_labeling_db_name>
   LABELING_DATABASE_USERNAME=<your_db_username>
   LABELING_DATABASE_PASSWORD=<your_db_password>
   LABELING_DATABASE_IP=<your_db_public_ip>
   LABELING_DATABASE_PORT=5432

   # Auth env variables
   TOKEN_ALGORITHM=<your_auth_token_algorithm>
   TOKEN_JWT_SECRET_KEY=<your_jwt_secret_key>
   TOKEN_JWT_SECRET_REFRESH_KEY=<your_jwt_secret_refresh_key>
   ALLOW_AUTH_ACCESS=true
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in jb-labeling-service folder of the repository in terminal:

```bash
  poetry run poe start
```

# 📃 3. API Specification and Documentation

### `GET /cases`

Returns the list of cases with case id and case name assigned to the given user

#### Successful Response

```json
[
  {
    "case_id": "",
    "case_name": ""
  }
]
```

#### What happens during the API call?

Once the API is hit, it validates the user details and fetches the case details assigned to the user from the database. Then it returns the cases with case id and case name as a list of dictionaries.

---

### GET `/cases/{case_id}`

Returns the details of a case for the given case id

#### Request

Requires a case_id(string).

#### Successful Response:

```json
{
  "case_id": "string",
  "case_name": "string",
  "case_type": "string",
  "court_name": "string",
  "court_type": "string",
  "doc_url": "string",
  "raw_text": "string",
  "doc_size": integer,
  "facts": "string",
  "facts_edited": boolean,
  "facts_last_updated_at": list,
  "facts_cumulative_time": integer,
  "facts_reviewed": boolean,
  "issues": list,
  "issues_edited": boolean,
  "issues_last_updated_at": list,
  "issues_cumulative_time": integer,
  "issues_reviewed": boolean,
  "generated_issues": "string",
  "sections": list,
  "sections_edited": boolean,
  "sections_last_updated_at": list,
  "sections_cumulative_time": integer,
  "sections_reviewed": boolean,
  "precedents": list,
  "precedents_edited": boolean,
  "precedents_last_updated_at": list,
  "precedents_cumulative_time": integer,
  "precedents_reviewed": boolean,
  "petitioner_arguments": list,
  "petitioner_arguments_edited": boolean,
  "petitioner_arguments_last_updated_at": list,
  "petitioner_arguments_cumulative_time": integer,
  "petitioner_arguments_reviewed": boolean,
  "generated_petitioner_arguments": "string",
  "respondent_arguments": list,
  "respondent_arguments_edited": boolean,
  "respondent_arguments_last_updated_at": list,
  "respondent_arguments_cumulative_time": integer,
  "respondent_arguments_reviewed": boolean,
  "generated_respondent_arguments": "string",
  "is_completed": boolean,
  "petitioner_name": "string",
  "respondent_name": "string"
}
```

#### What happens during the API call?

Once the API is hit, it validates the given case_id and fetches the respective case details from the database. Then it returns the case details as a dictionary.

---

### POST `/cases/{case_id}/facts`

Updates the facts in the case details and returns null when successfuly updated

#### Request

Requires a case_id(string) and a case object as a post body.

#### What happens during the API call?

Once the API is hit, it validates the user details and updates the facts of the given case in the databases with the given facts.

---

### POST `/cases/{case_id}/issues`

Updates the issues in case details and returns null when successfuly updated

#### Request

Requires a case_id(string) and a case object as a post body.

#### What happens during the API call?

Once the API is hit, it validates the user details and updates the issues of the given case in the databases with the given issues.

---

### POST `/cases/{case_id}/sections`

Updates the sections in case details and returns null when successfuly updated

#### Request

Requires a case_id(string) and a case object as a post body.

#### What happens during the API call?

Once the API is hit, it validates the user details and updates the sections of the given case in the databases with the given sections.

---

### POST `/cases/{case_id}/precedents`

Updates the precedents in case details and returns null when successfuly updated

#### Request

Requires a case_id(string) and a case object as a post body.

#### What happens during the API call?

Once the API is hit, it validates the user details and updates the precedents of the given case in the databases with the given precedents.

---

### POST `/cases/{case_id}/arguments`

Updates the arguments in case details and returns null when successfuly updated

#### Request

Requires a case_id(string) and a case object as a post body.

#### What happens during the API call?

Once the API is hit, it validates the user details and updates the arguments of the given case in the databases with the given arguments.

---

### GET `/generate-issues`

Returns the GPT generated issues for the given case id

#### Request

Requires a case_id(string).

#### Successful Response:

Returns a string of generated issues.

#### What happens during the API call?

Once the API is hit, it validates the given case_id and fetches the facts of the respective case details from the database. Then it uses the facts to generate issues using OpenAI's GPT-3.5-turbo mocdel and returns the generated issues as a string.

---

### GET `/generate-arguments`

Returns the GPT generated arguments for the given case id

#### Request

Requires a case_id(string) and generate_arguments_for(string).

#### Successful Response:

Returns a string of generated arguments.

#### What happens during the API call?

Once the API is hit, it validates the given case_id and fetches the facts, issues, sections and precedents of the respective case details from the database. Then it uses the fetched details to generate arguments using OpenAI's GPT-3.5-turbo mocdel and returns the generated arguments as a string.

# 🚀 4. Deployment

This repository comes with a Dockerfile which is present under the tools subfolder. You can use this dockerfile to deploy your version of this application to Cloud Run in GCP.
Make the necessary changes to your dockerfile with respect to your new changes. (Note: The given Dockerfile will deploy the base code without any error, provided you added the required environment variables (mentioned in the .env file) to either the Dockerfile or the cloud run revision). You can run the following command to build the docker image:

```bash
poetry run poe build
```

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
