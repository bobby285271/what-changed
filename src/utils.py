import subprocess


def get_eval(flakes_url, attr_path):
    return subprocess.run(['nix', 'eval', '--raw', rf"{flakes_url}#{attr_path}"],
                          stdout=subprocess.PIPE, text=True).stdout


def get_tagmap(repo):
    tagmap = {}
    for tag in repo.tags:
        tagmap.setdefault(repo.commit(tag), []).append(tag)
    return tagmap


def print_commit_tags(tagmap, commit, file):
    oup = open(file, 'a', encoding='utf-8')
    if commit in tagmap:
        oup.write("  - <sub>Tagged:")
        for tag in tagmap.get(commit):
            oup.write(f" <code>{tag}</code>")
        oup.write("</sub>\n")
    oup.close()
