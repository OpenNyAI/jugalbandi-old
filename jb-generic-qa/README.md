# Generic Q&A : Factual Question & Answering over arbitrary number of documents

[Generic Q&A](https://api.jugalbandi.ai/docs) is a system of APIs that allows users to build Q&A style applications on their private and public datasets. The system creates Open API 3.0 specification endpoints using FastAPI.

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

3. Once poetry is installed, go into the **jb-generic-qa** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

4. You will need a GCP account to store the uploaded documents & indices in a bucket and to host a postgres connection to store the api logs.

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

6. In addition to creating gcp_credentials.json file, create another file **.env** inside the jb-generic-qa folder which will hold the development credentials and add the following variables. Update the openai_api_key, path to gcp_credentials.json file, gcp_bucket_name and your db connections appropriately.

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   GOOGLE_APPLICATION_CREDENTIALS=<path_to_gcp_credentials.json>
   GCP_BUCKET_NAME=<your_gcp_bucket_name>
   GCP_BUCKET_FOLDER_NAME=<your_gcp_bucket_folder_name>
   DOCUMENT_LOCAL_STORAGE_PATH=local
   QA_DATABASE_NAME=<your_db_name>
   QA_DATABASE_USERNAME=<your_db_username>
   QA_DATABASE_PASSWORD=<your_db_password>
   QA_DATABASE_IP=<your_db_public_ip>
   QA_DATABASE_PORT=5432

   # Auth env variables
   ALLOW_AUTH_ACCESS=true
   TOKEN_ALGORITHM=<your_auth_token_algorithm>
   TOKEN_JWT_SECRET_KEY=<your_jwt_secret_key>
   TOKEN_JWT_SECRET_REFRESH_KEY=<your_jwt_secret_refresh_key>
   AUTH_DATABASE_IP=<your_db_public_ip>
   AUTH_DATABASE_PORT=5432
   AUTH_DATABASE_USERNAME=<your_db_username>
   AUTH_DATABASE_PASSWORD=<your_db_password>
   AUTH_DATABASE_NAME=<your_auth_db_name>

   # Tenant env variables
   TENANT_DATABASE_IP=<your_db_public_ip>
   TENANT_DATABASE_PORT=5432
   TENANT_DATABASE_USERNAME=<your_db_username>
   TENANT_DATABASE_PASSWORD=<your_db_password>
   TENANT_DATABASE_NAME=<your_tenant_db_name>
   ALLOW_INVALID_API_KEY=true

   # Speech processor and translator env variables
   BHASHINI_USER_ID=<your_bhashini_user_id>
   BHASHINI_API_KEY=<your_bhashini_api_key>
   BHASHINI_PIPELINE_ID=<your_bhashini_pipeline_id>
   ```

7. This service uses Auth service as well as other packages such as auth-token, tenant, speech processor, translator. Hence their respective environment variables are also required. Please refer to their respective repositories for more information.

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in jb-generic-qa folder of the repository in terminal

```bash
poetry run poe start
```

# 📃 3. API Specification and Documentation

### `POST /upload-files`

Returns an UUID number for a set of documents uploaded

#### Request

Requires at least one file (pdf, docx, txt or zip files) for uploading.

#### Successful Response

```json
{
  "uuid_number": "<36-character string>",
  "message": "Files uploading is successful"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, an uuid_number is created and the files are uploaded to the GCP bucket with the uuid_number as folder name. Immediately after this process, indexing of the files happen. Two types of indexing happen - one for gpt-index and the other for langchain. The two indexing processes produce three index files - index.json, index.faiss and index.pkl. These index files are again uploaded to the same GCP bucket folder under their respective subfolders(gpt-index and langchain) for using them during query time.

---

### `GET /query-with-gptindex`

#### Request

Requires an uuid_number(string) and query_string(string).

#### Successful Response

```json
{
  "query": "<your-given-query>",
  "answer": "<paraphrased-response>",
  "source_text": "<source-text-from-which-answer-is-paraphrased>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the **index.json** file is fetched from the GCP bucket provided the uuid_number given is correct. Once the **index.json** is successfully fetched, it is then used to answer the query given by the user.

---

### `GET /query-with-langchain` (uses GPT3 model)

#### Request

Requires an uuid_number(string) and query_string(string).

#### Successful Response

```json
{
  "query": "<your-given-query>",
  "answer": "<paraphrased-response>",
  "source_text": "<source-text-from-which-answer-is-paraphrased>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the **index.faiss** and **index.pkl** files are fetched from the GCP bucket provided the uuid_number given is correct. Once the index files are successfully fetched, they are then used to answer the query given by the user.

---

### `GET /query-with-langchain-gpt3-5` (uses GPT3.5-turbo model)

It performs the same way as `/query-with-langchain` endpoint. The only difference is that it uses GPT3.5-turbo model for querying process.

---

### `GET /query-with-langchain-gpt4` (uses GPT4 model)

#### Request

Requires an uuid_number(string) and query_string(string).

#### Successful Response

```json
{
  "query": "<your-given-query>",
  "answer": "<response>",
  "source_text": ""
}
```

It performs the same way as `/query-with-langchain-gpt3-5` endpoint.
One major difference here is that this api uses GPT4 model for querying process, hence the answer will not be paraphrased on most cases and precisely that is why the source_text will be empty in the response since we get the actual source_text present in the document as the answer in response.

---

### `GET /query-with-langchain-gpt3-5-custom-prompt` (uses GPT3.5-turbo model with custom prompts)

#### Request

Requires an uuid_number(string), a query_string(string) and an optional prompt(string) field.

#### Successful Response

```json
{
  "query": "<your-given-query>",
  "answer": "<paraphrased-response>",
  "source_text": ""
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, the **index.faiss** and **index.pkl** files are fetched from the GCP bucket provided the uuid_number given is correct. Once the index files are successfully fetched, then they are used along with the given prompt to answer the query given by the user.
The prompt gives personality to the LLM model and hence the answer will be generated based on the prompt given. If the prompt is not given, then the default prompt will be used.

---

### `GET /query-with-langchain-gpt4-custom-prompt` (uses GPT4 model with custom prompts)

It performs the same way as `/query-with-langchain-gpt3-5-custom-prompt` endpoint. The only difference is that it uses GPT4 model for querying process.

---

### `GET /query-using-voice` (uses GPT3.5-turbo model with voice input)

#### Request

Requires an uuid_number(string), input_language(Selection - English, Hindi, Bengali, Gujarati, Marathi, Oriya, Punjabi, Kannada, Malayalam, Tamil, Telugu) and output_format(Selection - Text, Voice).

Either of the query_text(string) or audio_url(string) should be present. If both the values are given, query_text is taken for consideration. Another requirement is that the input_language should be same as the one given in query_text and audio_url (i.e, if you select English in input_language, then your query_text and audio_url should contain queries in English). The audio_url should be publicly downloadable, otherwise the audio_url will not work.

#### Successful Response

```json
{
  "query": "<query-in-given-language>",
  "query_in_english": "<query-in-english>",
  "answer": "<paraphrased-answer-in-given-language>",
  "answer_in_english": "<paraphrased-answer-in-english>",
  "audio_output_url": "<publicly-downloadable-audio-output-url-in-given-language>",
  "source_text": "<source-text-from-which-answer-is-paraphrased-in-english>"
}
```

#### What happens during the API call?

Once the API is hit with proper request parameters, it is then checked for the presence of query_text.

If query_text is present, the translation of query_text based on input_language is done. Then the translated query_text is given to langchain model which does the same work as `/query-with-langchain-gpt3-5` endpoint. Then the paraphrased answer is again translated back to input_language. If the output_format is voice, the translated paraphrased answer is then converted to a mp3 file and uploaded to a GCP folder and made public.

If the query_text is absent and audio_url is present, then the audio url is downloaded and converted into text based on the input_language. Once speech to text conversion in input_language is finished, the same process mentioned above happens. One difference is that by default, the paraphrased answer is converted to voice irrespective of the output_format since the input_format is voice.

---

### `GET /query-using-voice-gpt4` (uses GPT4 model with voice input)

It performs the same way as `/query-using-voice` endpoint. The only difference is that it uses GPT4 model for querying process.

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

# 👩‍💻 6. Usage

To directly use the Jugalbandi APIs without cloning the repo, you can follow below steps to get you started:

1.  Visit [https://api.jugalbandi.ai/docs](https://api.jugalbandi.ai/docs).
2.  Scroll to the `/upload-files` endpoint to upload the documents.
3.  Once you have uploaded file(s) you should have received a `uuid number` for that document set. Please keep this number handy as it will be required for you to query the document set.
4.  Now that you have the `uuid number` you should scroll up to select the query endpoint you want to use. Currently, there are three different implementations we support i.e. `query-with-gptindex`, `query-with-langchain` (recommended), `query-using-voice` (recommended for voice interfaces). While you can use any of the query systems, we are constantly refining our langchain implementation.
5.  Use the `uuid number` and do the query.

## Feature request and contribution

- We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
- Kindly visit our project board to see what is it that we are prioritizing.
