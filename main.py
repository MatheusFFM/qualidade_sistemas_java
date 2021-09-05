import os

import requests
import subprocess
from git import Repo

headers = {"Authorization": "bearer Your GitHub API Token"}


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


def clone_repo(repo, file, directory):
    url = repo["url"]
    print(f"Cloning {file}...")
    Repo.clone_from(url, f'./{directory}/{file}')


def delete_repo(file, directory):
    print(f"Removing {file}...")
    subprocess.run(f"cd {directory} && rmdir /s /q {file}", shell=True)


def get_ck(file, directory):
    print(f"Analysing {file}...")
    path = f'{directory}/{file}'
    path_analytics = f'analytics/{file}'
    if not os.path.exists(path_analytics):
        os.mkdir(path_analytics)
    path_output = f'analytics/{file}/{file}'
    subprocess.call(["java", "-jar", "ckCalc.jar", path, "true", "0", "True", path_output])


def process_repos(query_result):
    directory = 'repos'
    for repo in query_result:
        file = repo["nameWithOwner"].replace("/", "")
        if not os.path.exists(f'analytics/{file}'):
            clone_repo(repo, file, directory)
            get_ck(file, directory)
            delete_repo(file, directory)


def clear():
    analytics_path = "analytics"
    if not os.path.exists(analytics_path):
        os.mkdir(analytics_path)
    repos_path = "repos"
    subprocess.run(f"rmdir /s /q {repos_path}", shell=True)
    os.mkdir(repos_path)


def main():
    clear()
    pages = 10
    after_code = None
    for page in range(pages):
        print(f"\n========== Page {page + 1} ==========\n")
        result = run_query(after_code)
        process_repos(result["data"]["search"]["nodes"])
        has_next = result["data"]["search"]["pageInfo"]["hasNextPage"]
        if not has_next:
            break
        after_code = result["data"]["search"]["pageInfo"]["endCursor"]


if __name__ == "__main__":
    main()
