# JB Streamlit UI

This is a streamlit UI service which helps with user registration, creation and management of knowledge base in a custom UI. The data collected by this service is then uploaded to DB which is then used by the Whatsapp script for custom bot creation.

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

3. Once poetry is installed, go into the **jb-streamlit-ui** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

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
   TENANT_DATABASE_NAME=<your_db_name>
   TENANT_DATABASE_USERNAME=<your_db_username>
   TENANT_DATABASE_PASSWORD=<your_db_password>
   TENANT_DATABASE_IP=<your_db_public_ip>
   TENANT_DATABASE_PORT=5432
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in jb-streamlit-ui/jugalbandi/streamlit-ui folder of the repository in terminal:

```bash
  streamlit run Create_Knowledge_Base.py
```

# 🚀 3. Deployment

This service comes with a Dockerfile which is present in the root folder. You can use this dockerfile to deploy your version of this streamlit UI application to Cloud Run in GCP.
Make the necessary changes to your dockerfile with respect to your new changes. (Note: The given Dockerfile will deploy the base code without any error, provided you added the required environment variables (mentioned in the .env file) to either the Dockerfile or the cloud run revision). You can run the following command to build the docker image:

```bash
poetry run poe build
```
