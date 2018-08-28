#!/usr/bin/python3

import argparse
import json
import subprocess
import urllib.request



def find_forks(remote):
    """
    Query the GitHub API for all forks of a repository.
    """
    repo_url = subprocess.run(
        ["git", "remote", "get-url", remote],
        stdout=subprocess.PIPE
    )

    # convert git@github.com:akumria/all_forks.git to
    # service: git@github.com
    # username: akumria
    # project = all_forks
    (service, repo) = str(repo_url.stdout).split(":")
    (username, project_git) = repo.split("/")
    project = project_git[:project_git.find(".")]

    GITHUB_FORK_URL = u"https://api.github.com/repos/{username}/{project}/forks"

    resp = urllib.request.urlopen(GITHUB_FORK_URL.format(username=username, project=project))
    
    resp_json = json.loads(resp.read())
    for fork in resp_json:
        yield (fork['owner']['login'], fork['ssh_url'])


def setup_remote(remote, repository_url):
    """
    Configure a remote with a specific repository.
    """
    print("{}: {}".format(remote, repository_url))
    subprocess.run(["git", "remote", "add", remote, repository_url])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote", help="Which remote to use", default="origin")
    args = parser.parse_args()

    for (remote, repository) in find_forks(args.remote):
        setup_remote(remote, repository)


if __name__ == "__main__":
    main()
