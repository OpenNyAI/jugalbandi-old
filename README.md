### Note: This repos is for low resource deployments. You can test it out by creating your own sample bot on our [test platform](https://test.jugalbandi.ai). For production level deployments please refer to newly architectured [Jugalbandi Manager](https://github.com/OpenNyAI/JB-Manager)

# Jugalbandi

Jugalbandi is home to several Jugalbandi services and packages for organisations to build and customize on top of them. This repository is structured in a way that it can be used as a monorepo for all the services and packages.

## Services

The following gives a brief description of each service in the repository. To know more in detail, please look into their respective folders.

### <b>Auth Service (jb-auth-service)</b>

The Auth service acts like a plug-n-play service in a way it can be plugged into any service which needs authentication mechanism. It uses basic login and signup endpoints to validate authentication.

### <b>Generic QnA (jb-generic-qa)</b>

The Generic QnA service is a collection of APIs which are used to do a factual question and answering over arbitrary number of documents. It uses LLMs to answer queries based on the given documents.

### <b>JIVA Service (jb-jiva-service)</b>

The JIVA service is specific to the JIVA (Judges' Intelligent Virtual Assistant) application which does provide the necessary endpoints and handles data. It uses FastAPI and PostgreSQL to achieve the task at hand.

### <b>Labeling Service (jb-labeling-service)</b>

Like JIVA service, the labeling serice is also unique to its own application Argument Generation. It also uses FastAPI and PostgreSQL to do its operations and provide the necessary endpoints for the application to consume.

## Packages

The packages contain several individual poetry packages which are plug and play components that can be plugged into several services thereby avoiding duplicity. To know more about each package, please look into their respective folders.

## Setup

The repository comes with a code-workspace file `jb.code-workspace` which can be used to open the entire repository in VSCode. The workspace file contains all the necessary settings and configurations to use the repository in VSCode. This can also be customized to suit your needs.

## New Updates

1. Categorized the project structure to have packages and services in the repository.
2. Added `jb-auth-service`, `jb-jiva-service`, `jb-labeling-service` and several individual packages to the repository.
3. All services and packages are now using `poetry` for dependency management.
4. Added `jb.code-workspace` file to open the repository in VSCode.

## Raise an Issue

To raise an issue, follow the template in `ISSUES_TEMPLATE.md` file which is present in the docs folder and create a new issue.

## Raise a Pull Request

To raise a PR, follow the template in `PULL_REQUEST_TEMPLATE.md` file which is present in the docs folder and create a new PR.
