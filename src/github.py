# GitHub specific stuff.

def print_title(name, url, from_rev, to_rev, file):
    oup = open(file, 'a', encoding='utf-8')
    oup.write(
        f"\n### [{name}]({url}): [{from_rev} → {to_rev}]({url}/compare/{from_rev}...{to_rev})\n\n")
    oup.close()


def print_commit(url, commit, file):
    oup = open(file, 'a', encoding='utf-8')
    msg = commit.message.splitlines()[0]
    oup.write(
        f"- [ ] [<code>{msg}</code>]({url}/commit/{commit.hexsha})\n")
    oup.close()
