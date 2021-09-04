import requests
import subprocess
from git import Repo

headers = {"Authorization": ""}


def run_query(after):
    after_formatted = "null" if after is None else "\"" + after + "\""
    query = """
    {
        search(query:"language:java", type: REPOSITORY, first: 1, after:""" + after_formatted + """) {
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


def clone_repo(repo, file, directory):
    url = repo["url"]
    print(f"Cloning {file}...")
    Repo.clone_from(url, f'./{directory}/{file}')


def delete_repo(file, directory):
    subprocess.run(f"cd {directory} && rmdir /s /q {file}", shell=True)


def process_repos(query_result):
    directory = 'repos'
    for repo in query_result:
        file = repo["nameWithOwner"].replace("/", "")
        clone_repo(repo, file, directory)
        delete_repo(file, directory)


def main():
    pages = 2
    after_code = None
    for page in range(pages):
        print(f"\n========== Page {page + 1} ==========\n")
        result = run_query(after_code)
        process_repos(result["data"]["search"]["nodes"])
        print_query_result(result)
        has_next = result["data"]["search"]["pageInfo"]["hasNextPage"]
        if not has_next:
            break
        after_code = result["data"]["search"]["pageInfo"]["endCursor"]


if __name__ == "__main__":
    main()
