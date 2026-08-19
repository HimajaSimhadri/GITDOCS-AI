import os


# ==========================================
# Supported File Types
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
# Ignored Directories
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

    ".idea",
    ".vscode",

}


# ==========================================
# Ignored Files
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
# Maximum File Size
# ==========================================

MAX_FILE_SIZE = 1_000_000


# ==========================================
# Read Repository
# ==========================================

def read_repository(repo_path):

    documents = []


    for root, dirs, files in os.walk(
        repo_path
    ):

        # ==================================
        # Ignore Directories
        # ==================================

        dirs[:] = [

            directory

            for directory in dirs

            if directory
            not in IGNORED_DIRECTORIES

        ]


        # ==================================
        # Read Files
        # ==================================

        for filename in files:


            if filename in IGNORED_FILES:

                continue


            extension = os.path.splitext(

                filename

            )[1].lower()


            if extension not in (
                SUPPORTED_EXTENSIONS
            ):

                continue


            file_path = os.path.join(

                root,

                filename

            )


            # ==================================
            # File Size Check
            # ==================================

            try:

                file_size = os.path.getsize(
                    file_path
                )

            except Exception:

                continue


            if file_size > MAX_FILE_SIZE:

                print(
                    f"Skipping large file: "
                    f"{file_path}"
                )

                continue


            # ==================================
            # Read Content
            # ==================================

            try:

                with open(

                    file_path,

                    "r",

                    encoding="utf-8",

                    errors="ignore"

                ) as file:

                    content = file.read()


                if not content.strip():

                    continue


                relative_path = (
                    os.path.relpath(

                        file_path,

                        repo_path

                    )
                )


                documents.append({

                    "path":
                    relative_path,

                    "content":
                    content

                })


            except Exception as error:

                print(

                    f"Could not read "
                    f"{file_path}: "
                    f"{error}"

                )


    print(

        f"Repository reader found "
        f"{len(documents)} useful files."

    )


    return documents