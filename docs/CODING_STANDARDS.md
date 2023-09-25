# Coding Standards for components

- Components should raise their own custom exceptions, not http exceptions.
- Packages should depend on wider range of versions, applications can use latest versions of python / dependencies.

# Notes

- Use ABC and abstractmethod wherever possible
- Use Nested exception and exception groups - never swallow an exception
- Always use async functions wherever possible.
  - i.e use httpx not requests, gcloud-aio-storage vs google-cloud-storage etc, google async clients
- Use conftest.py for tests (pytest.mark.asyncio)
- Key Safety - Do not put any secrets or key json files in the repository. Use environment variables or config files.
