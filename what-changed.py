#!/usr/bin/env python3

from git import Repo
import os
import sys
import src.utils as utils
import src.github as github

# Pantheon updates always target the `master` branch
nixpkgs_flakes = "github:NixOS/nixpkgs"
work_dir = os.path.join(os.path.dirname(__file__), 'work')
input_file = os.path.join(os.path.dirname(
    __file__), 'data', rf'{sys.argv[1]}.list')
output_file = os.path.join(os.path.dirname(__file__), rf'{sys.argv[1]}.md')

# Note that we only check whether one of these strings is prefix
# of the given commit message.
ignored_keyphrases = [
    'Translated using Weblate',
    'Added translation using Weblate',
    'Deleted translation using Weblate',
    'Update translation files',
    'Update translation template'  # Authored by @elementaryBot.
]


def get_dirpath(repo_url: str) -> str:
    return os.path.join(work_dir, repo_url.split('/')[-1])


def print_title(content: str):
    oup = open(output_file, 'a', encoding='utf-8')
    oup.write(content + "\n")


def print_log_github(pkg_attr: str, repo_url: str, from_rev: str):
    # `from_rev` can be either tag names or git commit hexsha. I assume
    # length of tag names won't exceed 16. Full git commit hexsha sounds
    # too long for me.
    from_rev_for_display = from_rev[:16]

    # Not trying to replace `HEAD` with the actual git commit hexsha as
    # I only want the output file to be updated when some non-tranlation
    # commits are made or some tags are created.
    github.print_title(pkg_attr, repo_url,
                       from_rev_for_display, "HEAD", output_file)

    repo = Repo(get_dirpath(repo_url))
    tagmap = utils.get_tagmap(repo)

    for commit in repo.iter_commits(rf"{from_rev}..HEAD", reverse=True):
        commit_message_oneline = commit.message.splitlines()[0]
        if commit in tagmap or not utils.contains_prefix(commit_message_oneline, ignored_keyphrases):
            github.print_commit(repo_url, commit, output_file)
            utils.print_commit_tags(tagmap, commit, output_file)


def main():
    if os.path.exists(output_file):
        os.remove(output_file)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    inp = open(input_file, 'r', encoding='utf-8')
    for pkg_attr in inp.readlines():
        pkg_attr = rf"{pkg_attr}".strip()
        # Ignore line starts with '#' and blank line
        if not pkg_attr or pkg_attr[0] == '#':
            continue
        # Directly print line starts with '@' to output
        elif pkg_attr[0] == '@':
            print_title(pkg_attr[1:])
        # Track repositories that has no corresponding
        # packages in Nixpkgs, so far only GitHub repos
        # are supported
        elif 'github:' in pkg_attr:
            repo_url = pkg_attr.split(' ')[0].replace(
                "github:", "https://github.com/")
            from_rev = pkg_attr.split(' ')[1]
            pkg_attr = pkg_attr.split(' ')[0]
            utils.clone_repo(repo_url, get_dirpath(repo_url))
            print_log_github(pkg_attr, repo_url, from_rev)
        # Track packages updates
        else:
            repo_url = utils.get_eval(
                nixpkgs_flakes, f"{pkg_attr}.src.meta.homepage")
            from_rev = utils.get_eval(nixpkgs_flakes, f"{pkg_attr}.src.rev")
            utils.clone_repo(repo_url, get_dirpath(repo_url))
            if "github.com" in repo_url:
                print_log_github(pkg_attr, repo_url, from_rev)


if __name__ == "__main__":
    main()
