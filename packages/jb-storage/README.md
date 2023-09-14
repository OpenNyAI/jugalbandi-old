# JB Storage

This package takes care of the storage management. It does the storage operations like reading, writing, listing, deleting, etc. The Storage class is a boilerplate class that can be extended to create a new storage class. Currently Google Storage class and Local Storage class are implemented by extending the Storage class. The Storage class is used in various packages such as:

- The DocumentCollection class is a wrapper class that uses the Storage class to perform the storage operations.
- The Library class is another wrapper class that uses the Storage class to perform the storage operations.

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

3. Once poetry is installed, go into the **jb-storage** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the storage classes from this package by running the **storage.py** or **google_storage.py** file or export this package to other services to use the given storage class objects.
