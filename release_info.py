#!/usr/bin/env python3
"""
Bot for updating pysal news

TODO
- [x] hook up to crontab for personal use
- [ ] document
- [ ] run locally for a bit before automating updates of pysal.github.io

Notes
-----
This polls all pysal packages to identify the date of the latest
release.

The last releast date for the news site is also determined.
n
Any package with a release date after the date of the last news site
release is identified, and a news entry is created for the
pysal.org/news page.

The markdown file with the entry is created locally.
"""

import pickle
import requests


packages = [
    "access",
    "esda",
    "giddy",
    "inequality",
    "libpysal",
    "mapclassify",
    "mgwr",
    "momepy",
    "pointpats",
    "pysal",
    "segregation",
    "spaghetti",
    "spglm",
    "spint",
    "splot",
    "spopt",
    "spreg",
    "spvcm",
    "tobler",
]


def get_latest_commit_date(repo_owner="pysal", repo_name="pysal.github.io"):
    """Determine the date of the latest commit for a github repository.

    Arguments
    ---------
    repo_owner: str
      name of repository owner on Github

    repo_name:
      name of repository

    Returns
    ------
    date: str
      date of last commit
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            commits_info = response.json()
            if commits_info:
                return commits_info[0]["commit"]["committer"]["date"]
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def get_latest_github_release(repo_owner, repo_name):
    """Get information about latest release of a package."""

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    url = f"{url}/releases/latest"

    # Send an HTTP GET request to the API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        release_info = response.json()

        # Extract and return the latest release version
        latest_version = release_info["tag_name"]
        published_at = release_info["published_at"]
        return latest_version, published_at
    else:
        # If the request was not successful, print an error message
        msg = "Failed to fetch the latest release for"
        print(f"{msg} {repo_owner}/{repo_name}.")
        return None


def get_release_dates(packages=packages):
    """Get release dates for all packages."""
    info = {}
    for package in packages:
        info[package] = get_latest_github_release("pysal", package)

    pickle.dump(info, open("info.p", "wb"))


def update_needed(file_name="info.p"):
    """Check if any packages have been released after latest update of
    news."""
    get_release_dates()
    info = pickle.load(open(file_name, "rb"))
    news_date = get_latest_commit_date()
    updates = []
    for package in info:
        if info[package][1] > news_date:
            updates.append(package)
    return updates


def load_dict_from_pickle(filename="info.p"):
    """Load a dictionary from a pickled object in the specified file."""
    try:
        with open(filename, "rb") as file:
            # Load and return the dictionary from the pickled file
            return pickle.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except pickle.UnpicklingError:
        print(f"Error while unpickling the file {filename}.")
        return None


def write_release_note(content, package, tag, dir="news"):
    file_name = f"{dir}/{package}_{tag}.md"
    with open(file_name, "w") as out_file:
        out_file.write(content)


def create_release_note(package, info):
    """Create the release note markdown file for a package.

    Parameters
    ----------
    package: str
      package name

    info: dict
      information on package release and tags

    Returns
    -------
    None

    This will create a markdown file with the release notes.

    """
    otag, _date = info[package]
    tag = otag.replace("v", "")
    front = _date.split("T")[0]
    year, month, day = front.split("-")
    month = month + "." + day
    url = f"https://github.com/pysal/{package}/releases/tag/{otag}"
    lines = []
    lines.append("---")
    lines.append(f"title: {package} {tag}")
    lines.append(f"date: {front}")
    lines.append(f"description: {package} {tag} released.")
    lines.append("type: news")
    lines.append(f'month: "{month}"')
    lines.append(f'year: "{year}"')
    lines.append(f'link: "{url}"')
    lines.append("---")
    content = "\n".join(lines)
    write_release_note(content, package, tag)


if __name__ == "__main__":
    pkgs_to_update = update_needed()
    if pkgs_to_update:
        info = load_dict_from_pickle()
        for pkg in pkgs_to_update:
            print(pkg)
            create_release_note(pkg, info)
