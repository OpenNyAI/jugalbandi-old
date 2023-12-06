# JB Translator

This is a package that takes care of translation of text. It has the following services:

- Bhashini (Dhruva APIs)
- Google
- Azure
- Composite (Combination of Bhashini, Google and Azure for better availability)

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

3. Once poetry is installed, go into the **jb-translator** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the classes from this package by running the **translator.py** file or export this package to other services to use it. To run directly, you will need to create a **.env** file in the **jb-translator** folder or in **the root folder of any other service** which uses this package and add the following environment variables:

```bash
GOOGLE_APPLICATION_CREDENTIALS=<path_to_gcp_credentials.json>
BHASHINI_USER_ID=<your_bhashini_user_id>
BHASHINI_API_KEY=<your_bhashini_api_key>
BHASHINI_PIPELINE_ID=<your_bhashini_pipeline_id>
AZURE_TRANSLATION_KEY=<your_azure_translation_key>
AZURE_TRANSLATION_RESOURCE_LOCATION=<your_azure_translation_resource_location>
```
