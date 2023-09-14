# Coding Standards for components

- components should raise their own custom exceptions, not http exceptions.
- packages should depend on wider range of versions, applications can use latest versions of python / dependencies

# Notes

- ABC, abstractmethod
- nested exception - never swallow an exception
- sync vs async - use httpx not requests, gcloud-aio-storage vs google-cloud-storage etc, google async clients
- use of conftest.py (pytest.mark.asyncio)
- faker
- key safety - do not put json file in
- exception group
- make components not depend on http
- protocols
- task groups

- virus issue in uploading files
- DDOS attacks - file size check
- why make blobs public?
