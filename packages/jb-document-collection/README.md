# JB Document Collection

This is a package that takes care of the documents uploaded by the user and stores them along with their index files as a single collection entity. It does the following operations:

- Creates a collection entity with its id as the **uuid number** of the given documents
- Reads and writes the document files to the cloud storage
- Reads and writes the index files to the cloud storage

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

3. Once poetry is installed, go into the **jb-document-collection** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the document collection and document repository classes from this package by running the **repository.py** file or export this package to other services to use the given two class objects.
