import logging
from jugalbandi.library import Library, DocumentMetaData, DocumentFormat
from jugalbandi.legal_library.csv_import import import_act_docs


async def test_library_import(
    jiva_library: Library,
    import_lib: str,
    caplog,
):
    caplog.set_level(level=logging.INFO)
    await import_act_docs(jiva_library, import_lib)
    # for lib_entry in lib_entries:
    #     md = DocumentMetaData(
    #         title=lib_entry.doc_title,
    #         original_file_name=lib_entry.file_name,
    #         original_format=DocumentFormat.PDF,
    #     )

    #     logging.info(md.original_format)

    #     filepath = f"{import_lib}/{lib_entry.file_name}"
    #     with open(filepath, "rb") as f:
    #         content = f.read()

    #     await jiva_library.add_document(md, content)

    list = await jiva_library.catalog()
    for md in list:
        logging.info(list[md])
