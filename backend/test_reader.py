from repo_reader import read_repository


repo_path = "repositories/Online-Exam-Portall"

documents = read_repository(repo_path)


print("\n================================")
print("FILES FOUND:", len(documents))
print("================================\n")


for document in documents:

    print("FILE:", document["path"])

    print("CONTENT PREVIEW:")
    print(document["content"][:200])

    print("--------------------------------")