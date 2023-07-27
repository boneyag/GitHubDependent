from bs4 import BeautifulSoup
import requests
import logging
import time

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# Initiall thought was to scrap all at once. Since the process is long and could interrupt from the server errors
# run the process for each library separately

# lib_git_repos = frozenset([
#     'matplotlib/matplotlib',
#     'mwaskom/seaborn',
#     'numpy/numpy',
#     'pandas-dev/pandas',
#     'tensorflow/tensorflow',
#     'scikit-learn/scikit-learn'
# ])


def scrape_dependents():
    repo_list = []

    # for lib in lib_git_repos:
    count = 0
    # change the lib accordingly
    lib = 'matplotlib/matplotlib'
    lib_dep_url = f"https://github.com/{lib}/network/dependents"

    while lib_dep_url:
        logging.info(f"GET {lib_dep_url}")
        r = requests.get(lib_dep_url)

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            box_content = soup.find("div", "Box")

            # box_content.find_all("div", "Box-row")[0].find_all("a", "text-bold")[0]["href"]
            box_rows = box_content.find_all("div", "Box-row")
            for row in box_rows:
                repo_list.append(row.find_all("a", "text-bold")[0]["href"])
            count += len(repo_list)
            logging.info(f"Number of repos collected: {count}")

            try:
                with open('repo_list_mpl.txt', 'a+') as f:
                    f.write('\n'.join(str(item)[1:] for item in repo_list))
                    repo_list.clear()
            except IOError as e:
                logging.error(f"Could not write to repo_list. {e}")

            nav_content = soup.find("div", "paginate-container")
            nav_anchor = nav_content.find_all("a")
            for nav in nav_anchor:
                if nav.string == "Next":
                    lib_dep_url = nav["href"]
                    time.sleep(30)
                else:
                    lib_dep_url = None

        else:
            logging.error(r.raise_for_status())

    logging.info(f"Completed collecting dependent repos for {lib}")


def main():
    scrape_dependents()


if __name__ == '__main__':
    main()
