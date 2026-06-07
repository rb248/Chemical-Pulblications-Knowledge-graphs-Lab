import json
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/graphql")
async def graphql_endpoint(request: Request):
    payload = await request.json()
    query = payload.get("query", "")

    # 1. Handle SPARQL query
    if "runSparql" in query:
        if "fabio:JournalArticle" in query:
            # get_some_publication_wo_img
            result_data = {
                "results": {
                    "bindings": [
                        {
                            "doi": {"value": "10.1016/j.compchemeng.2023.108252"},
                            "article": {"value": "http://example.org/article/1"}
                        }
                    ]
                }
            }
        elif "skos:note" in query:
            # get_download_link_with_given_doi
            result_data = {
                "results": {
                    "bindings": [
                        {
                            "doi": {"value": "10.1016/j.compchemeng.2023.108252"},
                            "downloadURL": {"value": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"},
                            "article": {"value": "http://example.org/article/1"}
                        }
                    ]
                }
            }
        else:
            result_data = {"results": {"bindings": []}}

        return {
            "data": {
                "runSparql": json.dumps(result_data)
            }
        }

    # 2. Handle uploadFile mutation
    elif "uploadFile" in query:
        return {
            "data": {
                "uploadFile": {
                    "fileName": "mocked_file.png",
                    "subjectURI": "http://example.org/article/1",
                    "predicate": "http://purl.org/vocab/frbr/core#exemplar",
                    "fileURI": "http://example.org/files/mocked_file.png",
                    "hashURI": "http://example.org/hash/1"
                }
            }
        }

    return {"errors": [{"message": "Unknown query or mutation"}]}


if __name__ == "__main__":
    print("Running Mock ChemEngKG GraphQL Server on port 4001...")
    uvicorn.run(app, host="127.0.0.1", port=4001)
