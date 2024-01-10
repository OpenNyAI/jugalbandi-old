import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.llms.openai import OpenAI
from langchain.chains import LLMChain
from jugalbandi.core.errors import (
    InternalServerException,
    ServiceUnavailableException
)
from jugalbandi.document_collection import DocumentCollection


async def rephrased_question(user_query: str):
    template = (
        """Write the same question as user input and """
        """make it more descriptive without adding """
        """new information and without making the facts incorrect.

    User: {question}
    Rephrased User input:"""
    )
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt,
                         llm=OpenAI(temperature=0, model="gpt-3.5-turbo-instruct"),
                         verbose=False)
    response = llm_chain.predict(question=user_query)
    return response.strip()


async def querying_with_langchain(document_collection: DocumentCollection,
                                  query: str,
                                  prompt: str,
                                  model_name: str):
    await document_collection.download_index_files("langchain", "index.faiss",
                                                   "index.pkl")
    index_folder_path = document_collection.local_index_folder("langchain")
    try:
        search_index = FAISS.load_local(index_folder_path,
                                        OpenAIEmbeddings())  # type: ignore
        documents = search_index.similarity_search(query, k=5)
        contexts = [document.page_content for document in documents]
        augmented_query = augmented_query = (
                "Information to search for answers:\n\n"
                "\n\n-----\n\n".join(contexts) +
                "\n\n-----\n\nQuery:" + query
            )

        if prompt != "":
            system_rules = prompt
        else:
            system_rules = (
                "You are a helpful assistant who helps with answering questions "
                "based on the provided information. If the information cannot be found "
                "in the text provided, you admit that I don't know"
            )
        res = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_rules},
                {"role": "user", "content": augmented_query},
            ],
        )
        return res["choices"][0]["message"]["content"]

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
