import importlib
import git

import wc_utils


def print_trivial(txt: str, file: str):
    oup = open(file, 'a', encoding='utf-8')
    oup.write(txt + "\n")
    oup.close()


def print_logs(kind: str, base: str, name: str, url: str,
               from_rev: str, to_rev: str, const_file: str, file: str):
    fmt = importlib.import_module(f"wc_{kind}")
    fmt.print_title(name, url, from_rev, to_rev, file)

    repo = git.Repo(wc_utils.get_dirpath(base, url))
    tagmap = wc_utils.get_tagmap(repo)
    igr_commit = wc_utils.get_const(const_file, "ignored_msg")

    for commit in repo.iter_commits(f"{from_rev}..{to_rev}", reverse=True):
        msg = commit.message.splitlines()[0]
        if commit in tagmap or not wc_utils.contains_prefix(msg, igr_commit):
            fmt.print_commit(url, commit, file)
            print_commit_tags(tagmap, commit, file)
            print_important_files(const_file, commit, file)
            print_important_keywords(const_file, repo, commit, file)


def print_items(key: str, lst: list, file: str):
    oup = open(file, 'a', encoding='utf-8')
    if lst:
        oup.write(f"  - <sub>{key}:")
        for i in lst:
            oup.write(f" <code>{i}</code>")
        oup.write("</sub>\n")
    oup.close()


def print_commit_tags(tagmap: dict, commit: git.Commit, file: str):
    print_items("Tags", tagmap.get(commit), file)


def print_important_files(const_file: str, commit: git.Commit, file: str):
    imp = wc_utils.get_const(const_file, "important_files")
    important_files = wc_utils.get_important_files(commit, imp)
    print_items("Files", important_files, file)


def print_important_keywords(const_file: str, repo: git.Repo, commit: git.Commit, file: str):
    imp = wc_utils.get_const(const_file, "important_keywords")
    important_keywords = wc_utils.get_important_keywords(repo, commit, imp)
    print_items("Keywords", important_keywords, file)
