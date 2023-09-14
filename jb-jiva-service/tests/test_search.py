import pytest
from jiva.search import preprocess_query, query_doc_titles, query_sections


@pytest.mark.asyncio
async def test_preprocessing_of_doc_query():
    query = "Give me the karnataka professional Educational institutions act"
    preprocessed_query = await preprocess_query(query)
    assert preprocessed_query == "the karnataka professional Educational institutions act"


@pytest.mark.asyncio
async def test_query_doctitles():
    query = "Give me debt relief act 2018"
    result = await query_doc_titles(query)
    assert result[0][0] == "THE KARNATAKA DEBT RELIEF ACT, 2018"


@pytest.mark.asyncio
async def test_query_sections():
    query = "Give me section 19 bangalore development authority act"
    result = await query_sections(query)
    assert (result["Document Title"] == "THE BANGALORE DEVELOPMENT AUTHORITY ACT, 1976" and
            result["Full Section Name"] == "19. Upon sanction, declaration to be published giving particulars of land to be acquired." and
            result["Section Page Number"] == 26)


@pytest.mark.asyncio
async def test_query_sections_with_incorrect_input():
    query = "Give me section IT act"
    result = await query_sections(query)
    print(result)
    assert result["Detail"] == "Incorrect input query format"


@pytest.mark.asyncio
async def test_query_sections_with_abbreviated_input():
    query = "Give me section 4 of IT act"
    result = await query_sections(query)
    print(result)
    assert (result["Document Title"] == "The Information Technology Act, 2000" and
            result["Full Section Name"] == "4. Legal recognition of electronic records." and
            result["Section Page Number"] == 9)
