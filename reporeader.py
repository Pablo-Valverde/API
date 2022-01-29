from git.exc import GitCommandError
import git
import shutil


def pull(DIR_NAME, REMOTE_URL):
    for _ in range(0,2):

        repo = git.Repo.init(DIR_NAME)

        try:
            repo.delete_remote("origin")
        except GitCommandError:
            pass     

        try:
            origin = repo.create_remote("origin", REMOTE_URL)
            origin.fetch()
        except GitCommandError:
            return

        try:
            if origin.refs.__len__() > 0:
                origin.pull(origin.refs[0].remote_head)
            return
        except GitCommandError:
            shutil.rmtree(DIR_NAME, ignore_errors=True)
    raise RuntimeError("Couldn't pull '%s' to '%s'" % (REMOTE_URL, DIR_NAME))
