#!/usr/bin/env python3

import os
import sys
import json
import collections

import utils
import printer

flake = "local" if utils.debug else "github:NixOS/nixpkgs"

base_dir = os.path.join(os.path.dirname(__file__), os.pardir)
data_dir = os.path.join(base_dir, 'data')
work_dir = os.path.join(base_dir, 'work')

const_file = os.path.join(data_dir, 'constants.json')
in_file = os.path.join(data_dir, f'{sys.argv[1]}.json')
out_file = os.path.join(base_dir, f'{sys.argv[1]}.md')


def fill_data(i):
    if not "kind" in i:
        i['kind'] = "github"
    if not "to_rev" in i:
        i['to_rev'] = "HEAD"
    if "attr_path" in i and not "url" in i:
        i['url'] = utils.get_eval(flake, f"{i['attr_path']}.src.meta.homepage")
    if "attr_path" in i and not "from_rev" in i:
        i['from_rev'] = utils.get_eval(flake, f"{i['attr_path']}.src.rev")
    if "url" in i and not "attr_path" in i:
        i['attr_path'] = i['url'].split('/')[-1]


def main():
    if os.path.exists(out_file):
        os.remove(out_file)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    inp = open(in_file, 'r', encoding='utf-8')
    data = json.load(inp, object_pairs_hook=collections.OrderedDict)

    for i in data['case']:
        if "kind" in i and i['kind'] == "markdown":
            printer.print_trivial(i['content'], out_file)
            continue

        fill_data(i)
        utils.clone_repo(i['url'], utils.get_dirpath(work_dir, i['url']))
        printer.print_logs(i['kind'], work_dir, i['attr_path'], i['url'],
                           i['from_rev'], i['to_rev'], const_file, out_file)


if __name__ == "__main__":
    main()
