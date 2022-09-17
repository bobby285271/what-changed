import subprocess
import git
import os
import shutil
import json
import re


debug = False


def find_word(w):
    # https://stackoverflow.com/a/5320179
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def get_const(file: str, key: str):
    f = open(file, 'r', encoding='utf-8')
    data = json.load(f)
    return data[key]


def contains_prefix(s: str, lst: list) -> bool:
    for i in lst:
        if s.startswith(i):
            return True
    return False


def get_eval(flakes_url: str, attr_path: str):
    return subprocess.run(['nix', 'eval', '--raw', rf"{flakes_url}#{attr_path}"],
                          stdout=subprocess.PIPE, text=True).stdout


def get_dirpath(base: str, url: str) -> str:
    return os.path.join(base, url.split('/')[-1])


def clone_repo(url: str, path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    if debug:
        url = url.replace("github.com", "hub.fgit.ml")
    git.Repo.clone_from(url=url, to_path=path)


def get_tagmap(repo: git.Repo) -> dict:
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)
    return tagmap


def get_important_files(commit: git.Commit, file: list) -> list:
    ret = []
    changed = commit.stats.files.keys()
    for i in file:
        for j in changed:
            if os.path.basename(j) == i:
                ret.append(i)
                break
    return ret


def get_important_keywords(repo: git.Repo, commit: git.Commit, file: list) -> list:
    ret = []
    raw_diff = repo.git.show(commit.hexsha, '--format=oneline', '-U0')
    for i in file:
        if find_word(i)(raw_diff):
            ret.append(i)
    return ret
