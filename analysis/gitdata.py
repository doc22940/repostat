import pandas as pd
import pygit2 as git


class History:

    def __init__(self, repository: git.Repository, branch: str = "master"):
        self.repo = repository
        self.branch = branch
        self.cache = None
        self.mailmap = git.Mailmap.from_repository(self.repo)

    def map_signature(self, signature: git.Signature):
        try:
            mapped_signature = self.mailmap.resolve_signature(signature)
        except ValueError as e:
            name = signature.name
            email = signature.email
            if not name:
                name = "Empty Empty"
                # warnings.warn(f"{str(e)}. Name will be replaced with '{name}'")
            if not email:
                email = "empty@empty.empty"
                # warnings.warn(f"{str(e)}. Email will be replaced with '{email}'")
            return git.Signature(name, email, signature.time, signature.offset, 'utf-8')
        else:
            return mapped_signature

    def as_dataframe(self):
        data = self.fetch()
        df = pd.DataFrame(data)
        return df

    def fetch(self):
        repo_walker = self._get_repo_walker()
        records = []
        for commit in repo_walker:
            mapped_author_signature = self.map_signature(commit.author)
            records.append({'commit_sha': commit.hex,
                            # TODO: signature mapper
                            'author_name': mapped_author_signature.name,
                            'author_timestamp': commit.author.time,
                            'author_tz_offset': commit.author.offset
                            })
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
