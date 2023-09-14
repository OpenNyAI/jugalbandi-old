from .pipeline import (
    DocumentProcess,
)
from .pipeline_manager import PipelineManager, PipelineStatus
from .library import (
    Library,
    LibraryFileType,
    Document,
    DocumentSection,
    DocumentFormat,
    DocumentMetaData,
    DocumentSupportingMetadata,
)
from .tasks import (
    TaskManager,
)
from .simple_doc_pipeline import SimpleDocumentPipeline
from .ls_tasks import LabelStudioTaskManager, LabelStudioTaskProcess
from .sections import SectionPdf, SectionReview


def initialize_pipeline_manager() -> PipelineManager:
    pipeline_manager = PipelineManager()
    label_studio_task_manager = LabelStudioTaskManager()
    pipeline_manager.register_task_manager(label_studio_task_manager)
    return pipeline_manager


__all__ = [
    "Document",
    "DocumentProcess",
    "DocumentSection",
    "PipelineManager",
    "TaskManager",
    "SimpleDocumentPipeline",
    "LabelStudioTaskProcess",
    "PipelineStatus",
    "Library",
    "LibraryFileType",
    "DocumentFormat",
    "DocumentMetaData",
    "DocumentSupportingMetadata",
    "initialize_pipeline_manager",
    "SectionPdf",
    "SectionReview",
]
