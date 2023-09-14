# JIVA Service : Backend Service for JIVA(Judges' Intelligent Virtual Assistant)

[JIVA Service](https://jiva-service-fer6v2lowq-uc.a.run.app/library/docs) is a collection of APIs that are specific to the JIVA (Judges' Intelligent Virtual Assistant) application which provides the necessary endpoints for acts and law documents and handles their respective data. It uses FastAPI and PostgreSQL to achieve the task at hand.

_Note:_

- _The JIVA Service APIs require authentiation, so before proceeding to use the APIs, register a new user in_ [https://jiva-service-fer6v2lowq-uc.a.run.app/library/auth/docs](https://jiva-service-fer6v2lowq-uc.a.run.app/library/auth/docs) _and use the username and password for authentication._
- _An_ `Authorize` _button is there at the top corner in_ [https://jiva-service-fer6v2lowq-uc.a.run.app/library/docs](https://jiva-service-fer6v2lowq-uc.a.run.app/library/docs) _. Click on the_ `Authorize` _button and provide the username and password to login and authorize all the APIs._

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

3. Once poetry is installed, go into the **jb-jiva-service** folder and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

4. You will need a GCP account to store the uploaded law documents and their metadata in a bucket and to host a postgres connection to store the user data.

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
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "<your-client-cert-url>"
   }
   ```

6. In addition to creating gcp_credentials.json file, create another file **.env** inside the jb-jiva-service folder which will hold the development credentials and add the following variables. Update the openai_api_key, path to gcp_credentials.json file, gcp_bucket_name, your db connections and other environment variables appropriately.

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   GOOGLE_APPLICATION_CREDENTIALS=<path_to_gcp_credentials.json>

   #JIVA database env variables
   JIVA_DATABASE_NAME=<your_db_name>
   JIVA_DATABASE_USERNAME=<your_db_username>
   JIVA_DATABASE_PASSWORD=<your_db_password>
   JIVA_DATABASE_IP=<your_db_public_ip>
   JIVA_DATABASE_PORT=5432

   # Auth env variables
   ALLOW_AUTH_ACCESS=false
   TOKEN_ALGORITHM=<your_auth_token_algorithm>
   TOKEN_JWT_SECRET_KEY=<your_jwt_secret_key>
   TOKEN_JWT_SECRET_REFRESH_KEY=<your_jwt_secret_refresh_key>
   AUTH_DATABASE_IP=<your_db_public_ip>
   AUTH_DATABASE_PORT=5432
   AUTH_DATABASE_USERNAME=<your_db_username>
   AUTH_DATABASE_PASSWORD=<your_db_password>
   AUTH_DATABASE_NAME=<your_auth_db_name>

   # JIVA email env variables
   JIVA_EMAIL_API_KEY=<your_email_api_key>

   # JIVA url env variables
   JIVA_BASE_URL=<your_application_url>
   JIVA_SUB_URL=update-password

   # JIVA library env variables
   JIVA_LIBRARY_BUCKET=<library_bucket>
   JIVA_LIBRARY_PATH=<library_bucket_path>
   ```

7. This service uses Auth service as well as other packages such as jb-auth-token, jb-core, jb-library, jb-legal-library, jb-storage, etc. Hence their respective environment variables are also required. Please refer to their respective repositories for more information.

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in jb-jiva-service folder of the repository in terminal

```bash
poetry run poe start
```

You can then access the APIs and their specification in [http://localhost:8080/library/docs](http://localhost:8080/library/docs) and the auth ones in [http://localhost:8080/library/auth/docs](http://localhost:8080/library/auth/docs)

# 📃 3. API Specification and Documentation

### `GET /documents`

#### Request

N/A

#### Successful Response

```json
{
  "documents": [
    {
      "id": "<document-id>",
      "title": "<document-title>"
    }
  ]
}
```

#### What happens during the API call?

Once the API is hit,the catalog, mainitaining the documents, will look into the GCP storage for that particular bucket/folder and it will return the list of document metadata, which are essentially the documents present in the cloud.

---

### `GET /document-info/{document_id}`

#### Request

Requires a document_id(string).

#### Successful Response

```json
{
  "id": "<document-id>",
  "title": "<document-title>",
  "original_file_name": "<original-file-name>",
  "source": "<document-source>",
  "original_format": "<document-format>",
  "create_ts": 0,
  "publish_date": "<document-publish-date>",
  "public_url": "<document-public-url>",
  "thumbnail_url": "<document-thumbnail-url>",
  "related_entity": "<document-related-entity>",
  "related_entity_title": "<document-related-entity-title>",
  "extra_data": {}, # extra data of the document
  "supportings": {} # supporting documents
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the GCP storage will be searched for the particular document id. If document is found, then metadata of that particular document is returned.

---

### `GET /document-section-info/{document_id}`

#### Request

Requires a document_id(string).

#### Successful Response

```json
[
  {
    "Full section name": "<full-section-name>",
    "Section number": "<section-number>",
    "Section name": "<section-name>",
    "Start page": "<section-start-page>"
  }
]
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the GCP storage will be searched for the particular document id. If document is found, then table of contents, each content containing full section name, section name, section number and start page of the section, of that particular document is returned.

---

### `GET /document/{document_id}?page_number={page_number}`

#### Request

Requires a document_id(string) and page_number(string) is optional.

#### Successful Response

_pdf of the document(if page_number is not provided)_

else

_image of the page of the given page_number of the document_

#### What happens during the API call?

Once the API is hit with proper request parameters,the document public url is taken from the metadata of the document of that particular document_id; then the whole document is downloaded. If the page number is given, then only that particular page is returned as a png bytes, else the total document is returned as pdf bytes.

---

### `GET /act-info/{act_id}`

#### Request

Requires an act_id(string). A typical act_id is `<jurisdiction>-<act-no>-<act-year>`. All the three values are present in the
`/document-info/{document_id}` response.

#### Successful Response

```json
{
  "id": "<act-id>",
  "no": "<act-no>",
  "year": "<act-year>",
  "title": "<act-title>",
  "description": "<act-description>",
  "passing_date": "<act-passing-date>",
  "effective_from_date": "<act-effective-from-date>",
  "jurisdiction": "<act-jurisdiction>",
  "documents": [] # list of documents that comes under this particular act
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the act catalog, mainitaining the acts, will look into the GCP storage for that particular bucket/folder and it will return the list of act metadata, and filtration is done based on the given act_id.

---

### `GET /query`

#### Request

Requires a query(string).

#### Successful Response

```json
{
  "items": [
    {
      "query_item_type": "document",
      "metadata": {
        "id": "<document-id>",
        "title": "<document-title>",
        "original_file_name": "<document-file-name",
        "source": "<document-source>",
        "original_format": "<document-format>",
        "create_ts": 0,
        "publish_date": "<document-publish-date>",
        "public_url": "<document-url>",
        "thumbnail_url": "<document-thumbnail-url>",
        "related_entity": "<document-related-entity>",
        "related_entity_title": "<document-related-entity-title>",
        "extra_data": {}, # extra data of the document
        "supportings": {} # supporting documents
      }
    },
    {
      "query_item_type": "section",
      "metadata": {
        "id": "<section-id>",
        "title": "<section-title>",
        "original_file_name": "<section-original-file-name>",
        "source": "<section-source>",
        "original_format": "<section-format>",
        "create_ts": 0,
        "publish_date": "<section-publish-date>",
        "public_url": "<section-url>",
        "thumbnail_url": "<section-thumbnail-url>",
        "related_entity": "<section-related-entity>",
        "related_entity_title": "<section-related-entity-title>",
        "extra_data": {}, # extra data of the document
        "supportings": {} # supporting documents
      },
    }
  ]
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, it checks weather the query contains the keyword `section` using the regex. If it contains then it will search for `section` using the section.json present in the cloud storage, else it will look for document based on the query title by using simple cosine similarity to match the title.

---

### `GET /daily-activities/{email_id}`

#### Request

Requires an email_id.

#### Successful Response

```json
{
  "daily_activities": [
    {
      "date": "<message-date>",
      "activities": [
        {
          "message_id": "<message-id>",
          "activity": "<activity>",
          "title": "<user-query>",
          "time": "<message-time>"
        }
      ]
    }
  ]
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the conversation history for that particular email_id is obtained from the database. The conversation history is then reformatted to the required response format.

---

## `DELETE /daily-activities/{email_id}/{message_id}`

#### Request

Requires an email_id and the message_id of the user query message that is to be deleted.

#### Successful Response

```json
{
  "response": "Activity deleted successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the user query related to that message_id and its aligned response from the bot are deleted from the database.

---

### `GET /conversation-history/{email_id}`

#### Request

Requires an email_id.

#### Successful Response

```json
[
  {
    "email_id": "<user-email-id>",
    "message_id": "<message-id>",
    "message": "<user-query>",
    "sender": "user",
    "query": "<user-query>",
    "feedback": null,
    "message_date": "<message-date>",
    "message_time": "<message-time>"
  },
  {
    "email_id": "<user-email-id>",
    "message_id": "<message-id>",
    "message": "<bot-response>",
    "sender": "bot",
    "query": "<user-query>",
    "feedback": "<feedback>",
    "message_date": "<message-date>",
    "message_time": "<message-time>"
  }
]
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the conversation history for that particular email_id is obtained from the database.

---

## `DELETE /conversation-history/{email_id}`

#### Request

Requires an email_id.

#### Successful Response

```json
{
  "response": "Conversation is cleared successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the conversation history related to the given email_id is deleted from the database.

---

## `POST /conversation-history`

#### Request

Requires

```json
{
  "email_id": "<email-id>",
  "message": "<user-query/bot-response>>",
  "sender": "<user/bot>",
  "query": "<user-query>",
  "feedback": "<feedback>"
}
```

#### Successful Response

```json
{
  "response": "Conversation is inserted successfully",
  "chat_message_id": "<message-id>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the message json gets inserted into the database with a unique message id, message time and message date.

---

## `PUT /conversation-history`

#### Request

Requires

```json
{
  "email_id": "<user-email-id>",
  "message_id": "<message-id>",
  "feedback": "<feedback>"
}
```

#### Successful Response

```json
null
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the feedback associated with the message_id gets updated.

---

### `GET /bookmarks/{email_id}`

#### Request

Requires an email_id.

#### Successful Response

```json
[
  {
    "email_id": "<user-email-id>",
    "bookmark_id": "<bookmark-id>",
    "document_id": "<document-id>",
    "document_title": "<document-title>",
    "section_name": "<section-name>",
    "bookmark_name": "<bookmark-name>",
    "bookmark_note": "<bookmark-note>",
    "bookmark_page": <bookmark-page>,
    "bookmark_date": "<bookmark-date>",
    "bookmark_time": "<boomark-time>"
  }
]
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the bookmarks for that particular email_id is obtained from the database.

---

## `DELETE /bookmarks/{email_id}/{bookmark_id}`

#### Request

Requires email_id and bookmark_id.

#### Successful Response

```json
{
  "response": "Bookmark is deleted successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the bookmark related to the given bookmark_id and given email_id is deleted from the database.

---

## `POST /bookmarks`

#### Request

Requires

```json
{
  "email_id": "<user-email-id>",
  "document_id": "<document-id>",
  "document_title": "<document-title>",
  "section_name": "<section-name>",
  "bookmark_name": "<bookmark-name>",
  "bookmark_note": "<bookmark-note>",
  "bookmark_page": <bookmark-page>
}
```

#### Successful Response

```json
{
  "response": "bookmark is inserted successfully",
  "bookmark_id": "<bookmark-id>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the bookmark gets inserted into the database with a unique bookmark id, bookmark time and bookmark date.

---

## `PUT /bookmark`

#### Request

Requires

```json
{
  "email_id": "<user-email-id>",
  "bookmark_id": "<bookmark-id>",
  "document_id": "<document-id>",
  "document_title": "<document-title>",
  "section_name": "<section-name>",
  "bookmark_name": "<bookmark-name>",
  "bookmark_note": "<bookmark-note>",
  "bookmark_page": <bookmark-page>
}
```

#### Successful Response

```json
{
  "response": "Bookmark updated successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the bookmark with the modified information gets updated.

---

### `GET /opened-documents/{email_id}`

#### Request

Requires an email_id.

#### Successful Response

```json
[
  {
    "email_id": "<user-email-id>",
    "document_title": "<document-title>",
    "document_id": "<document-id>"
  }
]
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the list of recently opened documents for that particular email_id is obtained from the database.

---

## `DELETE /opened-documents/{email_id}`

#### Request

Requires email_id and document_id.

#### Successful Response

```json
{
  "response": "Opened documents are cleared successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the recently opened document related to the given document_id and given email_id is deleted from the database.

---

## `POST /opened-documents`

#### Request

Requires

```json
{
  "email_id": "<user-email-id>",
  "document_title": "<document-title>",
  "document_id": "<document-id>"
}
```

#### Successful Response

```json
{
  "response": "Opened documents are inserted successfully"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the document gets inserted into the database as a recently opened one.

---

# 🚀 4. Deployment

This repository comes with a Dockerfile which is present under the tools subfolder. You can use this dockerfile to deploy your version of this application to Cloud Run.
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

# 👩‍💻 6. Usage

To directly use the JIVA APIs without cloning the repo, you can follow below steps to get you started:

1.  Visit [https://jiva-service-fer6v2lowq-uc.a.run.app/library/docs](https://jiva-service-fer6v2lowq-uc.a.run.app/library/docs).
2.  Authorize using the `Authorize` button, using your username and password.
3.  Now you can access all the APIs following their respective specification and documentation.
