from github_loader import clone_repository

url = "https://github.com/HimajaSimhadri/Online-Exam-Portall"

path = clone_repository(url)

print("Repository path:")
print(path)