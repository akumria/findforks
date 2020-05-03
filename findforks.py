#!/usr/bin/python3

import argparse
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request


def find_forks(remote):
    """
    Query the GitHub API for all forks of a repository.
    """
    resp_json = []

    repo_url = subprocess.run(
        ["git", "remote", "get-url", remote],
        stdout=subprocess.PIPE
    )

    repo_url_stdout = repo_url.stdout.decode()

    (username, project) = parse_git_remote_output(repo_url_stdout)

    GITHUB_FORK_URL = u"https://api.github.com/repos/{username}/{project}/forks"

    try:
        resp = urllib.request.urlopen(GITHUB_FORK_URL.format(username=username, project=project))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise StopIteration

    resp_json += json.loads(resp.read())

    while github_resp_next_page(resp):
        resp = urllib.request.urlopen(github_resp_next_page(resp))
        resp_json += json.loads(resp.read())

    for fork in resp_json:
        yield (fork['owner']['login'], fork['ssh_url'])


def github_resp_next_page(resp):
    """
    Check to see if the GitHub response has a next link.

    If the response, look for the 'link' header and see if
    there is a value pointed to by next.
    """
    link_header = resp.getheader(u"link")

    if not link_header:
        return None

    rel_next = u'rel="next"'
    for link in link_header.split(u","):
        if rel_next in link:
            return link[link.find(u"<") + 1:link.rfind(u">")]

    return None


def parse_git_remote_output(repo_url):
    """
    Given a repository URL, split it into its component parts.

    convert git@github.com:akumria/all_forks.git to
        service: git@github.com
        username: akumria
        project = all_forks

    convert https://github.com/akumria/all_forks.git to
        service: git@github.com
        username: akumria
        project = all_forks
    """

    if repo_url.startswith("git@github.com"):
        (service, repo) = repo_url.split(":")
        (username, project_git) = repo.split("/")
        project = project_git[:project_git.find(".")]
        return (username, project)

    if repo_url.startswith("http"):
        o = urllib.parse.urlparse(repo_url)
        (_, username, project_git) = o.path.split("/")
        # also handle the case where there is no '.git'
        if project_git.find(".") < 0:
            project = project_git
        else:
            project = project_git[:project_git.find(".")]
        return (username, project)


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
