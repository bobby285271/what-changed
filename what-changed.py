#!/usr/bin/env python3

from git import Repo
import os
import sys
import src.utils as utils
import src.github as github
import src.printer as printer

nixpkgs_flakes = "local" if utils.debug else "github:NixOS/nixpkgs"
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
        elif pkg_attr[0] == '@':
            printer.print_trivial(pkg_attr, output_file)
        # Track repositories that has no corresponding
        # packages in Nixpkgs, so far only GitHub repos
        # are supported
        elif 'github:' in pkg_attr:
            repo_url = pkg_attr.split(' ')[0].replace(
                "github:", "https://github.com/")
            from_rev = pkg_attr.split(' ')[1]
            pkg_attr = pkg_attr.split(' ')[0]
            utils.clone_repo(repo_url, utils.get_dirpath(work_dir, repo_url))
            printer.print_logs("src.github", work_dir, pkg_attr, repo_url,
                               from_rev, "HEAD", ignored_keyphrases, output_file)
        # Track packages updates
        else:
            repo_url = utils.get_eval(
                nixpkgs_flakes, f"{pkg_attr}.src.meta.homepage")
            from_rev = utils.get_eval(nixpkgs_flakes, f"{pkg_attr}.src.rev")
            utils.clone_repo(repo_url, utils.get_dirpath(work_dir, repo_url))
            if "github.com" in repo_url:
                printer.print_logs("src.github", work_dir, pkg_attr, repo_url,
                                   from_rev, "HEAD", ignored_keyphrases, output_file)


if __name__ == "__main__":
    main()
