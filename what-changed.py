#!/usr/bin/env python3

import os
import sys
import src.utils as utils
import src.printer as printer

flake = "local" if utils.debug else "github:NixOS/nixpkgs"

base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, 'data')
work_dir = os.path.join(base_dir, 'work')

in_file = os.path.join(data_dir, rf'{sys.argv[1]}.list')
out_file = os.path.join(base_dir, rf'{sys.argv[1]}.md')

ignored_msg = utils.get_ignored_msg(os.path.join(data_dir, 'constants.json'))


def main():
    if os.path.exists(out_file):
        os.remove(out_file)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    inp = open(in_file, 'r', encoding='utf-8')
    for line in inp.readlines():
        line = f"{line}".strip()

        if not line or line[0] == '#':
            continue

        elif line[0] == '@':
            printer.print_trivial(line, out_file)

        elif line.startswith('github:'):
            url = line.split(' ')[0].replace("github:", "https://github.com/")
            from_rev = line.split(' ')[1]
            line = line.split(' ')[0]
            utils.clone_repo(url, utils.get_dirpath(work_dir, url))
            printer.print_logs("src.github", work_dir, line, url,
                               from_rev, "HEAD", ignored_msg, out_file)

        else:
            url = utils.get_eval(flake, f"{line}.src.meta.homepage")
            from_rev = utils.get_eval(flake, f"{line}.src.rev")
            utils.clone_repo(url, utils.get_dirpath(work_dir, url))
            if "github.com" in url:
                printer.print_logs("src.github", work_dir, line, url,
                                   from_rev, "HEAD", ignored_msg, out_file)


if __name__ == "__main__":
    main()
