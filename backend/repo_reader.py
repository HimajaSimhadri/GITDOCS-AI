import os


# ==========================================
# File types GitDocs AI should read
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".html",
    ".css",
    ".json",
    ".md",
    ".sql",
}


# ==========================================
# Folders we should ignore
# ==========================================

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "coverage",
}


# ==========================================
# Files we should ignore
# ==========================================

IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "composer.lock",
    "poetry.lock",
    "Pipfile.lock",
}


# ==========================================
# Read Repository
# ==========================================

def read_repository(repo_path):

    documents = []

    for root, dirs, files in os.walk(repo_path):

        # --------------------------------------
        # Ignore unnecessary directories
        # --------------------------------------

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRECTORIES
        ]


        # --------------------------------------
        # Read files
        # --------------------------------------

        for filename in files:

            # Ignore lock/config files that
            # contain huge dependency information
            if filename in IGNORED_FILES:
                continue


            # Get extension
            extension = os.path.splitext(
                filename
            )[1].lower()


            # Ignore unsupported extensions
            if extension not in SUPPORTED_EXTENSIONS:
                continue


            file_path = os.path.join(
                root,
                filename
            )


            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    content = file.read()


                # Ignore empty files
                if not content.strip():
                    continue


                # Relative path inside repository
                relative_path = os.path.relpath(
                    file_path,
                    repo_path
                )


                documents.append({
                    "path": relative_path,
                    "content": content
                })


            except Exception as error:

                print(
                    f"Could not read {file_path}: {error}"
                )


    print(
        f"Repository reader found "
        f"{len(documents)} useful files."
    )


    return documents