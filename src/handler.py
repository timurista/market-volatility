import boto3
from github import Github
import os
import json
import datetime
from fang_volatility_rank import write_fang_change


def cleanup_repo(repo):
    # get a list of files
    try:
        dir_contents = repo.get_dir_contents("stock_scores")
        print(dir_contents)
        file_count = 0
        max_files = 2
        dir_contents.reverse()
        for contents in dir_contents:
            print(contents.name)
            file_count += 1
            if contents.name:
                datepart = contents.name.split("___")[0]
                delta = (
                    datetime.datetime.fromisoformat(datepart) - datetime.datetime.now()
                )
                print(datepart, delta.days, file_count, max_files)
                if delta.days > 30 or file_count > max_files:
                    deleted_file = repo.delete_file(
                        contents.path,
                        "(cleanup) delete an old file",
                        contents.sha,
                        branch="develop",
                    )
                    print("DELETE FILE", deleted_file)
    except Exception as e:
        print(e)


def make_github_commit():
    GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
    print(GITHUB_ACCESS_TOKEN)
    g = Github(GITHUB_ACCESS_TOKEN)
    # for repo in g.get_user().get_repos():
    #     print(repo.name)
    # repo.edit(has_wiki=False)
    repo = g.get_repo("timurista/market-volatility")
    # contents = repo.get_contents("src/fang_volatility.json", ref="test")

    isonow = datetime.datetime.now().isoformat()
    new_file_name = f"stock_scores/{isonow}___fang_volatility.json"
    contents = ""
    with open("fang_volatility.json", "r") as f:
        contents = json.load(f)

    created_file = repo.create_file(
        new_file_name,
        f"Added stock volatility score for {isonow}",
        json.dumps(contents, indent=2),
        branch="develop",
    )
    print(created_file)

    cleanup_repo(repo)
    title = f"Update stock volatility scores for current timestamp: {isonow}"
    body = """
    Summary:
    Current stock prices are out of sync and need to be merged in

    Tests:
    - [x] run the initial run command to generate the files
    - [x] assert the json file is made
    """
    pr = repo.create_pull(title=title, body=body, head="develop", base="master")
    print(pr)
    # pr.create_review_comment("LGTM! :tada:", commit=created_file.sha, )

    res = pr.merge(commit_message=title, merge_method="squash")
    print(res)
    # merge the pr


def handler():
    write_fang_change()
    make_github_commit()
    return {"message": "success", "statusCode": 200}


if __name__ == "__main__":
    handler()
