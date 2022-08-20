#!/usr/bin/env python3

import os
import sys
import json
import collections

import wc_utils
import wc_printer
import wc_data

flake = "local" if wc_utils.debug else "github:NixOS/nixpkgs"

base_dir = os.path.join(os.path.dirname(__file__), os.pardir)
data_dir = os.path.join(base_dir, 'data')
work_dir = os.path.join(base_dir, 'work')

const_file = os.path.join(data_dir, 'constants.json')
in_file = os.path.join(data_dir, f'{sys.argv[1]}.json')
out_file = os.path.join(base_dir, f'{sys.argv[1]}.md')


def main():
    inp = open(in_file, 'r', encoding='utf-8')
    rdata = json.load(inp, object_pairs_hook=collections.OrderedDict)

    for i in rdata['case']:
        wc_data.fill_data(i, flake)
        wc_data.fail_fast_check(i, const_file)

    if os.path.exists(out_file):
        os.remove(out_file)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    for i in rdata['case']:
        if "kind" in i and i['kind'] == "markdown":
            wc_printer.print_trivial(i['content'], out_file)
            continue

        wc_utils.clone_repo(i['url'], wc_utils.get_dirpath(work_dir, i['url']))
        wc_printer.print_logs(i['kind'], work_dir, i['attr_path'], i['url'],
                           i['from_rev'], i['to_rev'], const_file, out_file)


if __name__ == "__main__":
    main()
