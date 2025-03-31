# gh-local-backup

The first step is downloading the github CLI app.
Installation instructions for each OS can be found here [link](https://github.com/cli/cli?tab=readme-ov-file#installation).

After installing, all you need to do is run the following:
```
python3 main.py
```

This will prompt you to login the first time you run it.
Alternatively you can login beforehand by running:
```
gh auth login
```

You can check what accounts you are logged in with:
```
gh auth status
```

This tool will automatically create a gh_backup directory in the current folder and clone all your public/private repos into a subdirectory. It will not clone forks by default.