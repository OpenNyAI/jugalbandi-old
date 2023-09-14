import logging
from typing import Dict, Tuple
from jugalbandi.document_collection.repository import DocumentSourceFile
import os
from jugalbandi.document_collection import DocumentRepository

test_dir = os.path.dirname(__file__)


async def test_upload(
    doc_repo: DocumentRepository,
    zip_source_random: Tuple[Dict[str, bytes], DocumentSourceFile],
    caplog,
):
    caplog.set_level(level=logging.INFO)
    exp_values, zip_src_file = zip_source_random
    doc_collection = doc_repo.new_collection()
    await doc_collection.init_from_files([zip_src_file])

    filenames = []
    async for filename in doc_collection.list_files():
        filenames.append(filename)
        content = await doc_collection.read_file(filename)
        if filename in exp_values.keys():
            assert content == exp_values[filename]

    assert len(filenames) == len(exp_values)


async def test_index(
    doc_repo: DocumentRepository,
    zip_source_random: Tuple[Dict[str, bytes], DocumentSourceFile],
    caplog,
):
    caplog.set_level(level=logging.INFO)
    _, zip_src_file = zip_source_random
    doc_collection = doc_repo.new_collection()
    await doc_collection.init_from_files([zip_src_file])

    exp_content = b"hahahahaha"

    await doc_collection.write_index_file("langchain", "index.faiss", exp_content)

    content = await doc_collection.read_index_file("langchain", "index.faiss")

    assert content == exp_content


async def test_index_fallback(
    doc_repo: DocumentRepository,
    zip_source_random: Tuple[Dict[str, bytes], DocumentSourceFile],
    caplog,
):
    caplog.set_level(level=logging.INFO)
    _, zip_src_file = zip_source_random
    doc_collection = doc_repo.new_collection()
    await doc_collection.init_from_files([zip_src_file])

    exp_content = b"hahahahaha"

    await doc_collection.write_file("index.faiss", exp_content)

    content = await doc_collection.read_index_file("langchain", "index.faiss")

    assert content == exp_content


async def test_index_download(
    doc_repo: DocumentRepository,
    zip_source_random: Tuple[Dict[str, bytes], DocumentSourceFile],
    caplog,
):
    caplog.set_level(level=logging.INFO)
    _, zip_src_file = zip_source_random
    doc_collection = doc_repo.new_collection()
    await doc_collection.init_from_files([zip_src_file])

    exp_content = b"hahahahaha"

    await doc_collection.write_index_file("langchain", "index.faiss", exp_content)
    await doc_collection.write_index_file("langchain", "index.pkl", exp_content)

    await doc_collection.download_index_files("langchain", "index.faiss", "index.pkl")

    with open(
        doc_collection.local_index_file_path("langchain", "index.faiss"), "rb"
    ) as f:
        content = f.read()
        assert content == exp_content

    with open(
        doc_collection.local_index_file_path("langchain", "index.pkl"), "rb"
    ) as f:
        content = f.read()
        assert content == exp_content
