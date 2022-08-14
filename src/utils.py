import subprocess


def get_eval(flakes_url, attr_path):
    return subprocess.run(['nix', 'eval', '--raw', rf"{flakes_url}#{attr_path}"],
                          stdout=subprocess.PIPE, text=True).stdout
