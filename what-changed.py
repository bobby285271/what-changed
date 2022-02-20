#!/usr/bin/env python3

from urllib.parse import urljoin, quote_plus
from git import Repo
import os
import subprocess

nixpkgs_flakes = "github:NixOS/nixpkgs"
work_dir = os.path.join(os.path.dirname(__file__), '.work')
input_file = os.path.join(os.path.dirname(__file__), 'packages.list')
output_file = os.path.join(os.path.dirname(__file__), 'README.md')

ignored_keyphrases = [
    'Translated using Weblate',
    'Added translation using Weblate',
    'Deleted translation using Weblate',
    'Update translation files',
    'Update translation template'
]


def multi_urljoin(*parts) -> str:
    return urljoin(parts[0], "/".join(quote_plus(part.strip("/"), safe="/")
                                      for part in parts[1:]))


def contains_ignored_keyphrases(commit_message: str) -> bool:
    for keyphrase in ignored_keyphrases:
        if keyphrase in commit_message:
            return True
    return False


def get_eval(attr: str) -> str:
    return subprocess.run(['nix', 'eval', '--raw', rf"{nixpkgs_flakes}#{attr}"],
                          stdout=subprocess.PIPE, text=True).stdout


def get_dirpath(repo_url: str) -> str:
    return os.path.join(work_dir, repo_url.split('/')[-1])


def clone_repo(repo_url: str) -> str:
    Repo.clone_from(url=repo_url, to_path=get_dirpath(repo_url))


def print_log(pkg_attr: str, repo_url: str, from_rev: str):
    oup = open(output_file, 'a', encoding='utf-8')
    oup.write(
        "\n\n" + rf"#### [{pkg_attr}]({repo_url}): [{from_rev} → HEAD]({repo_url}/compare/{from_rev}..HEAD)" + "\n\n\n\n")

    repo = Repo(get_dirpath(repo_url))
    for commit in repo.iter_commits(rf"{from_rev}..HEAD", reverse=True):
        commit_message_oneline = commit.message.splitlines()[0]
        if not contains_ignored_keyphrases(commit_message_oneline):
            oup.write(
                rf"- [ ] [<code>{commit_message_oneline}</code>]({repo_url}/commit/{commit.hexsha})" + "\n")


def main():
    if os.path.exists(output_file):
        os.remove(output_file)
    os.makedirs(work_dir)
    inp = open(input_file, 'r', encoding='utf-8')
    for pkg_attr in inp.readlines():
        if pkg_attr[0] == '#' or not pkg_attr.strip():
            continue
        pkg_attr = pkg_attr.strip()
        repo_url = get_eval(rf"{pkg_attr}.src.meta.homepage")
        from_rev = get_eval(rf"{pkg_attr}.src.rev")
        clone_repo(repo_url)
        print_log(pkg_attr, repo_url, from_rev)


if __name__ == "__main__":
    main()
