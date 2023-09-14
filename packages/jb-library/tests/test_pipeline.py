import logging
from jugalbandi.library import (
    PipelineManager,
    DocumentProcess,
    PipelineStatus,
    SimpleDocumentPipeline,
)
from unittest.mock import AsyncMock, patch

from jugalbandi.library.pipeline import Document


def test_pipeline_initialized(pipeline_manager: PipelineManager):
    task_manager = pipeline_manager.get_task_manager("label-studio")
    assert task_manager is not None


def error_side_effect(doc):
    raise NotImplementedError()


@patch.multiple(
    DocumentProcess,
    __abstractmethods__=set(),
    execute=AsyncMock(side_effect=error_side_effect),
)
@patch.multiple(Document, __abstractmethods__=set())
async def test_simple_pipeline_execution(pipeline_manager: PipelineManager):
    process = DocumentProcess()
    doc = Document()
    pipeline = SimpleDocumentPipeline("test-pipeline", [process])
    status = await pipeline.execute(doc)
    assert status == PipelineStatus.COMPLETED
