import subprocess
import git
import os
import shutil


def contains_prefix(s: str, lst: list) -> bool:
    for i in lst:
        if s.startswith(i):
            return True
    return False


def get_eval(flakes_url: str, attr_path: str):
    return subprocess.run(['nix', 'eval', '--raw', rf"{flakes_url}#{attr_path}"],
                          stdout=subprocess.PIPE, text=True).stdout


def clone_repo(url: str, path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    git.Repo.clone_from(url=url, to_path=path)


def get_tagmap(repo: git.Repo) -> dict:
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)
    return tagmap


def print_commit_tags(tagmap: dict, commit: git.Commit, file: str):
    oup = open(file, 'a', encoding='utf-8')
    if commit in tagmap:
        oup.write("  - <sub>Tagged:")
        for tag in tagmap.get(commit):
            oup.write(f" <code>{tag}</code>")
        oup.write("</sub>\n")
    oup.close()
