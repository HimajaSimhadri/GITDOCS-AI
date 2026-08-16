import os
import shutil
import stat
from git import Repo


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPOSITORIES_DIR = os.path.join(
    BASE_DIR,
    "repositories"
)


def remove_readonly(func, path, exc_info):
    """
    Make read-only files writable before deleting them.
    This helps avoid Windows WinError 5.
    """

    os.chmod(path, stat.S_IWRITE)

    func(path)


def clone_repository(github_url: str):

    repo_name = github_url.rstrip("/").split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    repo_path = os.path.join(
        REPOSITORIES_DIR,
        repo_name
    )

    print(f"Repository path: {repo_path}")

    # Create repositories directory
    os.makedirs(
        REPOSITORIES_DIR,
        exist_ok=True
    )

    # Remove previous repository
    if os.path.exists(repo_path):

        print("Removing previous repository...")

        try:

            shutil.rmtree(
                repo_path,
                onerror=remove_readonly
            )

        except PermissionError as error:

            raise PermissionError(
                f"Cannot remove existing repository folder: {repo_path}. "
                f"Close any programs using this folder and try again."
            ) from error

    print(
        f"Cloning repository: {github_url}"
    )

    # Clone repository
    Repo.clone_from(
        github_url,
        repo_path
    )

    print(
        f"Repository cloned to: {repo_path}"
    )

    return repo_path