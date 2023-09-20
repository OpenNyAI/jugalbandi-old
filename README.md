# Jugalbandi

This repository is home to several Jugalbandi services and packages for organisations to build and customize on top of them.

## Services

### `Auth Service (jb-auth-service)`

The Auth service acts like a plug-n-play service in a way it can be plugged into any service which needs authentication mechanism. It uses basic login and signup endpoints to validate authentication.

<br>

### `Generic QnA (jb-generic-qa)`

The Generic QnA service is a collection of APIs which are used to do a factual question and answering over arbitrary number of documents. It uses LLMs to answer queries based on the given documents.

<br>

### `JIVA Service (jb-jiva-service)`

The JIVA service is specific to the JIVA (Judges' Intelligent Virtual Assistant) application which does provide the necessary endpoints and handles data. It uses FastAPI and PostgreSQL to achieve the task at hand.

<br>

### `Labeling Service (jb-labeling-service)`

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
