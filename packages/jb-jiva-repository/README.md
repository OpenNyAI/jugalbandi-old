# JB Feedback

This is a package which contains the JIVA repository class and its DB settings. It is used to read and write the JIVA specific information such as conversation history, feedback and logs to the JIVA DB.

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

3. Once poetry is installed, go into the **jb-jiva-repository** folder under the **packages** folder in the terminal and run the following commands to install the dependencies and create a virtual environment:

   ```bash
   poetry install
   source .venv/bin/activate
   ```

# 👩‍💻 2. Usage

Once the above installation steps are completed, you can export this package to JIVA service to use the jiva repository class to perform DB operations in JIVA database.
