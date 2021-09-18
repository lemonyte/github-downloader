import requests


def get_repos(owner: str):
    if 'users/' not in owner and 'orgs/' not in owner:
        owner = 'users/' + owner
    url = f'https://api.github.com/{owner}/repos'
    response = requests.get(url, allow_redirects=True)
    repos = [r['name'] for r in response.json()]
    return repos


def get_real_name(owner: str, repo: str):
    repos = get_repos(owner)
    for r in repos:
        if r.lower() == repo:
            return r
    return repo


def download_zip(owner: str, repo: str, branch: str = 'main', dest: str = '.'):
    url = f'https://github.com/{owner}/{repo}/archive/{branch}.zip'
    with open(f'{dest}/{repo}-{branch}.zip', 'wb') as file:
        file.write(requests.get(url, allow_redirects=True).content)


if __name__ == '__main__':
    try:
        owner = str(input("Owner: "))
        repo = str(input("Repository (type $all to download all repos): "))
        branch = str(input("Branch: "))
        branch = 'main' if branch == '' else branch
        dest = str(input("Destination: "))
        dest = '.' if dest == '' else dest

        if repo == '$all':
            for repo in get_repos(owner):
                download_zip(owner, repo, branch, dest)
        else:
            download_zip(owner, get_real_name(owner, repo), branch, dest)
    except Exception as exception:
        print(f"Fatal error: {exception}")
