import openai
import json
from gpt_index import GPTSimpleVectorIndex
from jugalbandi.core.errors import InternalServerException, ServiceUnavailableException
from jugalbandi.document_collection import DocumentCollection


async def querying_with_gptindex(document_collection: DocumentCollection, query: str):
    index_content = await document_collection.read_index_file("gpt-index", "index.json")
    index_content = index_content.decode('utf-8')
    index_dict = json.loads(index_content)
    index = GPTSimpleVectorIndex.load_from_dict(index_dict)
    try:
        response = index.query(query)
        source_nodes = response.source_nodes
        source_text = []
        for i in range(len(source_nodes)):
            text = source_nodes[i].node.get_text().strip()
            source_text.append(text)
        return str(response).strip(), source_text
    except openai.error.RateLimitError as e:
        raise ServiceUnavailableException(
            f"OpenAI API request exceeded rate limit: {e}"
        )
    except (openai.error.APIError, openai.error.ServiceUnavailableError):
        raise ServiceUnavailableException(
            "Server is overloaded or unable to answer your request at the moment."
            " Please try again later"
        )
    except Exception as e:
        raise InternalServerException(e.__str__())
