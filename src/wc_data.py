import wc_utils


def fill_data(i, flake):
    if not "kind" in i:
        i['kind'] = "github"
    if not "to_rev" in i:
        i['to_rev'] = "HEAD"

    if "attr_path" in i and not "url" in i:
        i['url'] = wc_utils.get_eval(flake, f"{i['attr_path']}.src.meta.homepage")
    if "attr_path" in i and not "from_rev" in i:
        i['from_rev'] = wc_utils.get_eval(flake, f"{i['attr_path']}.src.rev")

    if "url" in i:
        i['url'] = i['url'].rstrip('/')
        if not "attr_path" in i:
            i['attr_path'] = i['url'].split('/')[-1]


def fail_fast_check(i, const_file):
    if not i['kind'] in wc_utils.get_const(const_file, "supported_kind"):
        exit(1)
    if i['kind'] != "markdown":
        if not "attr_path" in i or not "url" in i or not "from_rev" in i:
            exit(1)
    else:
        if not "content" in i:
            exit(1)
