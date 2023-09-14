# JB QA

This is a QnA package which has the gpt-index and langchain querying and indexing functions. This package is used by the Generic QA service to use its functionalities which are mentioned below:

- QAEngine acts as a wrapper for the gpt-index and langchain query functions.
- Indexer is used to index the documents for both gpt-index and langchain models.
- TextConverter is used to convert the pdf to the required text format for indexing.
- QADB is used to store the query logs. (Currently not used anywhere)

<br>

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

3. Once poetry is installed, go into the **jb-qa** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can use the desired functions from this package by running the respective files directly or export this package to other services (like Generic QA service) to use it. To use and run individual files directly, you will need to create a **.env** file in the **jb-qa** folder or in the **root folder of any other service** which uses this package and add the following environment variables:

```bash
# To do OpenAI calls
OPENAI_API_KEY=<your_openai_api_key>

# To read and write data to GCP bucket
GOOGLE_APPLICATION_CREDENTIALS=<path_to_gcp_credentials.json>
GCP_BUCKET_NAME=<your_gcp_bucket_name>
GCP_BUCKET_FOLDER_NAME=<your_gcp_bucket_folder_name>
DOCUMENT_LOCAL_STORAGE_PATH=local

# To connect to DB
QA_DATABASE_NAME=<your_db_name>
QA_DATABASE_USERNAME=<your_db_username>
QA_DATABASE_PASSWORD=<your_db_password>
QA_DATABASE_IP=<your_db_public_ip>
QA_DATABASE_PORT=5432
```
