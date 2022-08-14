#!/usr/bin/env python3

from git import Repo
import os
import subprocess
import shutil
import sys

# Pantheon updates always target the `master` branch
nixpkgs_flakes = "github:NixOS/nixpkgs"
work_dir = os.path.join(os.path.dirname(__file__), 'work')
input_file = os.path.join(os.path.dirname(__file__), 'data', rf'{sys.argv[1]}.list')
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


def startswith_ignored_keyphrases(commit_message: str) -> bool:
    for keyphrase in ignored_keyphrases:
        if commit_message.startswith(keyphrase):
            return True
    return False


def get_eval(attr: str) -> str:
    # Probably need nix-command and flakes as experimental features, but they
    # should be enabled by default already thanks to cachix/install-nix-action.
    return subprocess.run(['nix', 'eval', '--raw', rf"{nixpkgs_flakes}#{attr}"],
                          stdout=subprocess.PIPE, text=True).stdout


def get_dirpath(repo_url: str) -> str:
    return os.path.join(work_dir, repo_url.split('/')[-1])


def clone_repo(repo_url: str):
    Repo.clone_from(url=repo_url, to_path=get_dirpath(repo_url))


def print_title(content: str):
    oup = open(output_file, 'a', encoding='utf-8')
    oup.write(content + "\n")


def print_log_github(pkg_attr: str, repo_url: str, from_rev: str):
    # `from_rev` can be either tag names or git commit hexsha. I assume
    # length of tag names won't exceed 16. Full git commit hexsha sounds
    # too long for me.
    from_rev_for_display = from_rev[:16]
    oup = open(output_file, 'a', encoding='utf-8')
    # Not trying to replace `HEAD` with the actual git commit hexsha as
    # I only want the output file to be updated when some non-tranlation
    # commits are made or some tags are created.
    #
    # Print 3 extra blank lines here so I can write something on
    # these lines fast when the output is used in actual review.
    oup.write(
        "\n" + rf"### [{pkg_attr}]({repo_url}): [{from_rev_for_display} → HEAD]({repo_url}/compare/{from_rev}...HEAD)" + "\n\n\n\n")

    repo = Repo(get_dirpath(repo_url))
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)

    for commit in repo.iter_commits(rf"{from_rev}..HEAD", reverse=True):
        commit_message_oneline = commit.message.splitlines()[0]
        if commit in tagmap or not startswith_ignored_keyphrases(commit_message_oneline):
            # Prefixed with `- [ ]` to make this a task list.
            #
            # Commit messages are put in <code></code> blocks simply
            # because this is my personal preference.
            oup.write(
                rf"- [ ] [<code>{commit_message_oneline}</code>]({repo_url}/commit/{commit.hexsha})")
            if commit in tagmap:
                oup.write(" <sub>Tagged:")
                for tag in tagmap.get(commit):
                    oup.write(rf" <code>{tag}</code>")
                oup.write("</sub>")
            oup.write("\n")


def main():
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    if os.path.exists(output_file):
        os.remove(output_file)
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
            clone_repo(repo_url)
            print_log_github(pkg_attr, repo_url, from_rev)
        # Track packages updates
        else:
            repo_url = get_eval(rf"{pkg_attr}.src.meta.homepage")
            from_rev = get_eval(rf"{pkg_attr}.src.rev")
            clone_repo(repo_url)
            if "github.com" in repo_url:
                print_log_github(pkg_attr, repo_url, from_rev)


if __name__ == "__main__":
    main()
