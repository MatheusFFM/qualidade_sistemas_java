import requests
import csv

headers = {"Authorization": "Your Git API Token"}


def run_query(after):
    after_formatted = "null" if after is None else "\"" + after + "\""
    query = """
    {
        search(query:"language:java", type: REPOSITORY, first: 100, after:""" + after_formatted + """) {
            pageInfo {
              endCursor
              hasNextPage
            }
            nodes {
              ... on Repository {
                stargazerCount
                nameWithOwner
                createdAt
                url
                releases {
                  totalCount
                }
              }
            }
        }
    }
    """
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def print_query_result(query_result):
    result_format = query_result["data"]["search"]["nodes"]
    for rf in result_format:
        print(rf)


def save_on_file(query_result, writer):
    return False


pages = 10
afterCode = None
for page in range(pages):
    print(f"\n========== Page {page + 1} ==========\n")
    result = run_query(afterCode)
    print_query_result(result)
    has_next = result["data"]["search"]["pageInfo"]["hasNextPage"]
    if not has_next:
        break
    afterCode = result["data"]["search"]["pageInfo"]["endCursor"]