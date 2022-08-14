import subprocess
import git
import os
import shutil
import json


debug = False


def get_ignored_msg(file: str):
    f = open(file, 'r', encoding='utf-8')
    data = json.load(f)
    return data['ignored_msg']


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
        url = url.replace("github.com", "hub.0z.gs")
    git.Repo.clone_from(url=url, to_path=path)


def get_tagmap(repo: git.Repo) -> dict:
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)
    return tagmap
