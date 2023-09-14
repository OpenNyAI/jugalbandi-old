# JB Library

This is a generic library package that takes in a storage (eg: google storage) and performs the following operations:

- Read and write the documents along with their metadata and supporting documents to cloud storage
- Read and write the section data relatedd to the documents to cloud storage

This package has the Library class which is very generic and it can be extended to other use cases as well.

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

3. Once poetry is installed, go into the **jb-library** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the Library class from this package by running the **library.py** file or export this package to other services or packages (like Legal Library package) to use the given class.
