import os
import argparse
import requests


def get_repos(user: str, token: str = '') -> dict:
    if 'users/' not in user and 'orgs/' not in user:
        user = 'users/' + user
    return requests.get(f'https://api.github.com/{user}/repos', allow_redirects=True, auth=(user, token)).json()


def get_repo_json(user: str, repo_name: str, token: str = '') -> dict:
    repos = get_repos(user, token)
    for repo in repos:
        if repo['name'].casefold() == repo_name.casefold():
            return repo
    raise Exception(f"Repository '{repo_name}' not found")


def download_zip(user: str, repo: dict, branch: str = '', dest: str = '.', token: str = ''):
    branch = branch if branch else repo['default_branch']
    url = f"https://github.com/{user}/{repo['name']}/archive/{branch}.zip"
    response = requests.get(url, allow_redirects=True, auth=(user, token))
    content_type = response.headers['Content-Type']
    if content_type == 'application/zip':
        filename = response.headers['content-disposition'].split('=')[1]
    else:
        filename = f"{repo['name']}-{branch}.txt"
    with open(f'{dest}/{filename}', 'wb') as file:
        file.write(response.content)


def clone(user: str, repo: dict, dest: str = '.', token: str = ''):
    cwd = os.getcwd()
    os.chdir(dest)
    if token == '':
        os.system(f"git clone https://github.com/{user}/{repo['name']}.git")
    else:
        os.system(f"git clone https://{token}@github.com/{user}/{repo['name']}.git")
    os.chdir(cwd)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Download or clone GitHub repositories.")
        parser.add_argument('-u', '--user', default='', help="GitHub username")
        parser.add_argument('-r', '--repo', default='*', help="repository name, '*' for all repos, default is '*'")
        parser.add_argument('-b', '--branch', default='', help="repository branch, default is the default repo branch")
        parser.add_argument('-d', '--dest', default='.', help="destination directory, default is '.'")
        parser.add_argument('-t', '--token', default='', help="GitHub personal access token for private repos, default is ''")
        parser.add_argument('-o', '--operation', default='zip', choices=['zip', 'clone', 'list'], help="operation to execute, 'zip', 'clone', or 'list', default is 'zip'")
        args = parser.parse_args()
        user, repo, branch, dest, token, operation = vars(args).values()
        if not user:
            user = input("Username: ").strip()
            repo = input("Repository (enter '*' to download all repos): ").strip()
            repo = repo if repo else '*'
            branch = input("Branch: ").strip()
            dest = input("Destination: ").strip()
            dest = dest if dest else '.'
            token = input("Token: ").strip()
            operation = input("Operation ('zip', 'clone', or 'list'): ").strip().lower()
            if not user:
                raise Exception("Please enter a valid GitHub username")
            if operation not in ['zip', 'clone', 'list']:
                raise Exception("Please enter a valid operation: 'zip', 'clone', or 'list'")
        if operation == 'list':
            print(f"Repositories for user '{user}':")
            for repo in get_repos(user, token):
                print(f"name: {repo['name']}, default branch: {repo['default_branch']}, private: {repo['private']}")
        elif operation == 'zip':
            if repo == '*':
                for repo in get_repos(user, token):
                    download_zip(user, repo, branch, dest, token)
            else:
                download_zip(user, get_repo_json(user, repo, token), branch, dest, token)
        elif operation == 'clone':
            if repo == '*':
                for repo in get_repos(user, token):
                    clone(user, repo, dest, token)
            else:
                clone(user, get_repo_json(user, repo, token), dest, token)
    except Exception as exception:
        print(f"Fatal error: {exception}")
