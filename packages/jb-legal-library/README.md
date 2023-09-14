# JB Legal Library

This is a package that is used in the JIVA service which does the following operations:

- Storing the act informations to cloud storage
- Searching for the acts and their sections

This package extends the Library class from the generic **jb-library** package and it is specific to the JIVA service. That is precisely why it is named **jb-legal-library**.

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

3. Once poetry is installed, go into the **jb-legal-library** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 🏃🏻 2. Running

Once the above installation steps are completed, you can directly use the Legal Library from this package by running the **legal_library.py** file or export this package to other services (like JIVA service) to use the given class.
