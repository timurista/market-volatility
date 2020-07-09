import boto3
from github import Github
import os
import json
import datetime
from fang_volatility_rank import write_fang_change


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
    res = repo.create_file(
        new_file_name,
        f"Added stock volatility score for {isonow}",
        json.dumps(contents),
        branch="master",
    )
    # res = repo.update_file(contents.path, "more tests", "more tests", contents.sha, branch="test")
    print(res)


def handler():
    write_fang_change()
    make_github_commit()
    return {"message": "success", "statusCode": 200}


if __name__ == "__main__":
    handler()
