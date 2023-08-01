from gh_support import analyze_patterns
from github import Github

from datetime import datetime
import time
import logging
import json
import os

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def filter_repos():
    disc_repos = set()
    candidate_repos = set()

    with open('config.json') as cf:
        config = json.load(cf)

    with open('unique_repos.txt') as f:
        repo_names = f.readlines()

    if os.path.exists('discarded_repos.txt'):
        with open('discarded_repos.txt') as f:
            disc_repo_names = f.readlines()
            for r in disc_repo_names:
                disc_repos.add(r.strip())

    gh = Github(config["gh_auth_token"])

    for item in repo_names:
        repo_name = item.strip()
        if repo_name not in disc_repos or repo_name not in candidate_repos:
            logging.info(f"Accessing {repo_name}")

            rate_limit = gh.get_rate_limit()
            core_rate_limit = rate_limit.core
            search_rate_limit = rate_limit.search

            logging.info(f"Remaining GitHub API requests: {core_rate_limit.remaining}/{core_rate_limit.limit}")

            if core_rate_limit.remaining == 1:
                reset_time_core = core_rate_limit.reset
                current_time = datetime.now()
                delta = (reset_time_core - current_time).seconds
                logging.info(f"Rate limit reset on {reset_time_core.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info(f"Sleep for {delta} seconds")

                logging.info(f"Writing candidate repos and discarded repos to files")
                with open('candidate_repos.txt', 'a+') as f:
                    for cand in candidate_repos:
                        f.write(f"{cand}\n")
                with open('discarded_repos.txt', 'a+') as f:
                    for disc in disc_repos:
                        f.write(f"{disc}\n")

                time.sleep(delta)

            if search_rate_limit.remaining == 1:
                reset_time_search = search_rate_limit.reset
                current_time = datetime.now()
                delta = (reset_time_search - current_time).seconds
                logging.info(f"Secondary rate limit reset on {reset_time_search.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info(f"Sleep for {delta} seconds")

                logging.info(f"Writing candidate repos  and discarded repos to files")
                with open('candidate_repos.txt', 'a+') as f:
                    for cand in candidate_repos:
                        f.write(f"{cand}\n")
                with open('discarded_repos.txt', 'a+') as f:
                    for disc in disc_repos:
                        f.write(f"{disc}\n")

                time.sleep(delta)

            repo = gh.get_repo(repo_name)

            # not archived
            if repo.archived:
                disc_repos.add(repo_name)
                continue
            # not a private
            if repo.private:
                disc_repos.add(repo_name)
                continue
            # not a fork
            if repo.fork:
                disc_repos.add(repo_name)
                continue

            # topic analysis - does not contain education, tutorial, example
            topics = repo.get_topics()
            if analyze_patterns(topics):
                disc_repos.add(repo_name)
                continue

            # description analysis - does not contain education, tutorial, example
            desc = repo.description
            if analyze_patterns(desc):
                disc_repos.add(repo_name)
                continue

            # activity - eliminate test repositories
            date_created = repo.created_at
            last_committed = repo.pushed_at
            delta = (last_committed - date_created).days
            if delta < 2:
                disc_repos.add(repo_name)
                continue

            # contributors - eliminate personal repositories
            if repo.get_contributors().totalCount == 1:
                disc_repos.add(repo_name)
                continue

            candidate_repos.add(repo_name)


def main():
    filter_repos()


if __name__ == '__main__':
    main()
