import pandas as pd
import pygit2 as git


class History:

    def __init__(self, repository: git.Repository, branch: str = "master"):
        self.repo = repository
        self.branch = branch
        self.cache = None

    def as_dataframe(self):
        data = self.fetch()
        return pd.DataFrame(data)

    def fetch(self):
        records = []
        for commit in self.repo.walk(self.repo.head.target, git.GIT_SORT_TOPOLOGICAL):
            records.append({'commit_sha': commit.hex, 'author_timestamp': commit.author.time})
        return records

    # abstract method
    def _get_repo_walker(self):
        pass


class WholeHistory(History):
    def _get_repo_walker(self):
        return self.repo.walk(self.repo.head.target, git.GIT_SORT_TOPOLOGICAL)


class LinearHistory(History):
    def _get_repo_walker(self):
        linear_walker = self.repo.walk(self.repo.head.target, git.GIT_SORT_TOPOLOGICAL)
        linear_walker.simplify_first_parent()
        return linear_walker
