
import os
import sys
import subprocess
import json
from pathlib import Path
from multiprocessing import Pool
from datetime import datetime
from functools import partial
import shutil

def run(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def noisy_run(command):
    res = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")

    print("Return Code: ", res.returncode)
    print("Stdout: ", res.stdout)
    print("Stderr: ", res.stderr)
    
    return res

def check_gh_install():
    res = run("gh")
    if res == 1:
        print("Please install the github CLI tool. https://github.com/cli/cli?tab=readme-ov-file#installation")
        print("For Example:")
        print("    Windows:")
        print("        winget install --id GitHub.cli")
        print("        scoop install gh")
        print("        choco install gh")
        print("    Mac:")
        print("        brew install gh")
        print("    Ubuntu:")
        print("        sudo apt install gh")

def check_login():
    res = run(["gh", "auth", "status"])

    if res.returncode ==  1:
        return False
    return True

def login():
    if check_login():
        return

    while True:
        command = ["gh", "auth", "login"]
        res = subprocess.run(command, shell=True)

        if res.returncode == 0:
            break
        else:
            print("Login failed, please try again... ")

    return

def repo_list():
    # gh repo list USER_OR_ORG --json name,owner,url
    res = run(["gh","repo","list", "-L", "4", "--source", "--json", "name,url"])
    
    return json.loads(res.stdout) 

def create_dest_dir(dest_path):
    dest_path = Path(dest_path)
    dest_path.mkdir(parents=True, exist_ok=True)
    count = max(1, len(os.listdir(dest_path)))
    dest_path /= f'backup_{count}_{datetime.now().strftime('%Y-%m-%d_%Hh_%Mm_%Ss')}'
    dest_path.mkdir(parents=True, exist_ok=True)
    
    return dest_path

def clone_repo(url, dest_path):
    print('Cloning ', url)
    subprocess.run(["git", "clone", url], cwd=dest_path, shell=True, capture_output=True)

def clone_repos(repos, dest_path):
    dest_path = str(dest_path.resolve())

    clone_with_dest = partial(clone_repo, dest_path=dest_path)
    with Pool() as pool:
        results = list(pool.map(clone_with_dest, [r['url'] for r in repos]))

    # for r in repos:
    #     print(r['url'])
    #     subprocess.run(["git", "clone", r['url']], cwd=dest_path, shell=True)

def compress_dest(dest_path):
    dest_path = Path(dest_path)
    arc_path = dest_path / '..' / 'archive'
    print(arc_path)
    arc_path.mkdir(parents=True, exist_ok=True)
    dest_path = arc_path / dest_path.parts[-1]
    shutil.make_archive(dest_path, 'zip', arc_path)

def remove_uncompressed_dest(dest_path):
    try:
        shutil.rmtree(dest_path)
    except PermissionError as e:
        print(f"PermissionError: {e}")

# By default all public and private repos are backed up, but not forks
# TODO:
# 1. options:
#     * clone forks
#     * clone submodules
# 2. browsing an archive in a (simple gh-like) UI
# 3. resyncing (but should it push/pull or make a new backup etc.)
def main():
    dest_path = './gh_backup'

    # handle args, sys.argv

    # check_gh_install()
    # login()

    repos = repo_list()
    dest_path = create_dest_dir(dest_path)

    print('Cloning Repositories...')
    clone_repos(repos, dest_path)
    print('Finished Cloning Repositories...')

    print('Compressing Result...')
    compress_dest(dest_path)

    # print('Removing Uncompressed Result...')
    # remove_uncompressed_dest(dest_path)
    print('Done...')



if __name__ == '__main__':
    main()