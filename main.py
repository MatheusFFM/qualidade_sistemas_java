import os

import requests
import subprocess
import csv
import pandas as pd
from git import Repo
from datetime import datetime
from dateutil.relativedelta import relativedelta

headers = {"Authorization": "bearer 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"}


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
    subprocess.call(["java", "-jar", "ckCalc.jar", path, "true", "0", "False", path_output])


def get_api_data(data):
    name = data["nameWithOwner"]
    stars = data["stargazerCount"]
    releases = data["releases"]["totalCount"]
    created_at = datetime.fromisoformat(data["createdAt"][0:10])
    today = datetime.utcnow()
    age = relativedelta(today, created_at).years
    return [name, stars, releases, age]


def get_ck_data(name, folder):
    if not os.path.exists(folder):
        return []
    name = name.replace("/", "")
    class_file = f"{folder}/{name}class.csv"
    if os.stat(class_file).st_size > 0:
       class_data = pd.read_csv(class_file, encoding="ISO-8859-1")
       loc = class_data["loc"].sum()
       cbo = class_data["cbo"].median()
       dit = class_data["dit"].median()
       lcom = round(class_data["lcom*"].median(), 2)
       return [loc, cbo, dit, lcom]
    return []


def already_exists(name, results_file):
    data = pd.read_csv(results_file)
    return name in list(data["Name"])


def save_repo(repo, writer, folder_cks, results_file):
    repo_name = repo["nameWithOwner"]
    if not already_exists(repo_name, results_file):
        ck_data = get_ck_data(repo_name, folder_cks)
        if len(ck_data) > 0:
            print(f"Saving {folder_cks}...")
            api_data = get_api_data(repo)
            data = api_data + ck_data
            writer.writerow(data)


def process_repos(query_result):
    directory = 'repos'
    for repo in query_result:
        file = repo["nameWithOwner"].replace("/", "")
        results_file_name = 'results.csv'
        if not os.path.exists(f'analytics/{file}'):
            clone_repo(repo, file, directory)
            get_ck(file, directory)
            delete_repo(file, directory)
        with open(results_file_name, mode='a+') as results_file:
            writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            save_repo(repo, writer, f'analytics/{file}', results_file_name)


def clear():
    analytics_path = "analytics"
    if not os.path.exists(analytics_path):
        os.mkdir(analytics_path)
    repos_path = "repos"
    subprocess.run(f"rmdir /s /q {repos_path}", shell=True)
    if not os.path.exists(repos_path):
        os.mkdir(repos_path)


def setup_results():
    results_file = 'results.csv'
    if not os.path.exists(results_file):
        with open(results_file, mode='w') as results_file:
            writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['Name', 'Stars', 'Releases', 'Age', 'LOC', 'CBO', 'DIT', 'LCOM']
            writer.writerow(header)


def main():
    clear()
    setup_results()
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
