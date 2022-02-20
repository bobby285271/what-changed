#!/usr/bin/env python3

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


def startswith_ignored_keyphrases(commit_message: str) -> bool:
    for keyphrase in ignored_keyphrases:
        if commit_message.startswith(keyphrase):
            return True
    return False


def get_eval(attr: str) -> str:
    return subprocess.run(['nix', 'eval', '--raw', rf"{nixpkgs_flakes}#{attr}"],
                          stdout=subprocess.PIPE, text=True).stdout


def get_dirpath(repo_url: str) -> str:
    return os.path.join(work_dir, repo_url.split('/')[-1])


def clone_repo(repo_url: str) -> str:
    Repo.clone_from(url=repo_url, to_path=get_dirpath(repo_url))


def print_title(content: str):
    oup = open(output_file, 'a', encoding='utf-8')
    oup.write(content + "\n")


def print_log(pkg_attr: str, repo_url: str, from_rev: str):
    oup = open(output_file, 'a', encoding='utf-8')
    oup.write(
        "\n\n" + rf"#### [{pkg_attr}]({repo_url}): [{from_rev} → HEAD]({repo_url}/compare/{from_rev}...HEAD)" + "\n\n\n\n")

    repo = Repo(get_dirpath(repo_url))
    for commit in repo.iter_commits(rf"{from_rev}..HEAD", reverse=True):
        commit_message_oneline = commit.message.splitlines()[0]
        if not startswith_ignored_keyphrases(commit_message_oneline):
            oup.write(
                rf"- [ ] [<code>{commit_message_oneline}</code>]({repo_url}/commit/{commit.hexsha})" + "\n")


def main():
    if os.path.exists(output_file):
        os.remove(output_file)
    os.makedirs(work_dir)
    inp = open(input_file, 'r', encoding='utf-8')
    for pkg_attr in inp.readlines():
        pkg_attr = rf"{pkg_attr}".strip()
        if not pkg_attr or pkg_attr[0] == '#':
            continue
        elif pkg_attr[0] == '@':
            print_title(pkg_attr[1:])
        else:
            repo_url = get_eval(rf"{pkg_attr}.src.meta.homepage")
            from_rev = get_eval(rf"{pkg_attr}.src.rev")
            clone_repo(repo_url)
            print_log(pkg_attr, repo_url, from_rev)


if __name__ == "__main__":
    main()
