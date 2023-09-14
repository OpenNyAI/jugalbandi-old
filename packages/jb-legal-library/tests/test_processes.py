import logging
import os
from jugalbandi.library.processes import _extract_sections


def test_section():
    dirname = os.path.dirname(__file__)
    filename = f"{dirname}/import_lib/abcd.pdf"
    content = _extract_sections(filename)
    print(content)
