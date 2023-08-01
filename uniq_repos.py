import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

file_names = frozenset([
    'repo_list_mp.txt',
    'repo_list_sb.txt',
    'repo_list_sk.txt',
    'repo_list_tf.txt'
])


def filter_dup_repos():
    unique_repo_names = set()
    for item in file_names:
        with open(item) as f:
            repo_names = f.readlines()

            logging.info(f"Number of repos in {item}: {len(repo_names)}")

            for repo_name in repo_names:
                unique_repo_names.add(repo_name.strip())

    logging.info(f"Number of unique repos: {len(unique_repo_names)}")

    with open('unique_repos.txt', 'a+') as f:
        for repo_name in unique_repo_names:
            f.write(f"{repo_name}\n")

def main():
    filter_dup_repos()


if __name__ == "__main__":
    main()