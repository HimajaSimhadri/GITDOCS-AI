import os
import shutil
import stat

from git import Repo


# ==========================================
# Repository Directory
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

REPOSITORIES_DIR = os.path.join(
    BASE_DIR,
    "repositories"
)


# ==========================================
# Remove Read-Only Files
# ==========================================

def remove_readonly(
    func,
    path,
    exc_info
):

    os.chmod(
        path,
        stat.S_IWRITE
    )

    func(path)


# ==========================================
# Clone Repository
# ==========================================

def clone_repository(
    github_url: str
):

    repo_name = (
        github_url
        .rstrip("/")
        .split("/")[-1]
    )


    if repo_name.endswith(".git"):

        repo_name = repo_name[:-4]


    repo_path = os.path.join(

        REPOSITORIES_DIR,

        repo_name

    )


    print(
        f"Repository path: {repo_path}"
    )


    # ======================================
    # Create Directory
    # ======================================

    os.makedirs(

        REPOSITORIES_DIR,

        exist_ok=True

    )


    # ======================================
    # Remove Previous Repository
    # ======================================

    if os.path.exists(repo_path):

        print(
            "Removing previous repository..."
        )

        try:

            shutil.rmtree(

                repo_path,

                onerror=remove_readonly

            )

        except PermissionError as error:

            raise PermissionError(

                f"Cannot remove existing "
                f"repository folder: "
                f"{repo_path}. "
                f"Close any programs using "
                f"this folder and try again."

            ) from error


    # ======================================
    # Clone
    # ======================================

    print(
        f"Cloning repository: "
        f"{github_url}"
    )


    Repo.clone_from(

        github_url,

        repo_path

    )


    print(
        f"Repository cloned to: "
        f"{repo_path}"
    )


    return repo_path