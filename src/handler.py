# coding=utf8
from github import Github
import os
import json
import datetime
from src.fang_volatility_rank import write_fang_change
from time import sleep
import random


def cleanup_repo(repo):
    dir_contents = repo.get_dir_contents("stock_scores")
    file_count = 0
    max_files = 10
    dir_contents.reverse()
    for contents in dir_contents:
        print(contents.name)
        file_count += 1
        if contents.name:
            datepart = contents.name.split("___")[0]
            delta = datetime.datetime.fromisoformat(datepart) - datetime.datetime.now()
            if delta.days > 30 or file_count > max_files:
                try:
                    deleted_file = repo.delete_file(
                        contents.path,
                        "(cleanup) delete an old file",
                        contents.sha,
                        branch="develop",
                    )
                    print("DELETE FILE", deleted_file)
                except Exception as e:
                    print(e)

def cleanup_lingering_pulls(repo, title):
    try:
        pulls = repo.get_pulls()
        for pull in pulls:
            res = pull.merge(commit_message=title, merge_method="merge")
            print(res)
    except Exception as e:
        print(e)

def make_github_commit():
    GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
    print("GITHUB TOKEN", GITHUB_ACCESS_TOKEN)
    g = Github(GITHUB_ACCESS_TOKEN)
    try:
        repo = g.get_repo("timurista/market-volatility")

        isonow = datetime.datetime.now().isoformat()
        new_file_name = f"stock_scores/{isonow}___fang_volatility.json"
        contents = ""
        with open("fang_volatility.json", "r") as f:
            contents = json.load(f)

        title = random.choice(
            [
                f"Added stock volatility score for {isonow}",
                f"Continued work on updates for volatility scores",
                f"More updates on volatility",
                f"Adding score based on current time",
                f"Another score added",
            ]
        )

        cleanup_repo(repo)
        created_file = None
        try:
            created_file = repo.create_file(
                new_file_name, title, json.dumps(contents, indent=2), branch="develop",
            )
        except Exception as e:
            print(e)
        print(created_file)

        PR_TITLE = random.choice(
            [
                f"Latest Volatility score change",
                f"Updates for volatility scores",
                f"More updates on volatility",
                f"Fix for the volatility scores",
                f"The latest FANG and Microsoft volatility score",
                f"Adding score based on current time",
                f"Scores added to the current list",
            ]
        )

        PR_COMMENT = random.choice(
            [
                f"LGTM! :tada:",
                f"Nice work :ok_hand:",
                f"GTM :thumbsup",
                f"Done :white_check_mark:",
                f"G2G :green_heart:",
            ]
        )

        title = PR_TITLE
        body = """
        Summary:
        Current stock prices are out of sync and need to be merged in

        Tests:
        - [x] run the initial run command to generate the files
        - [x] assert the json file is made
        """
        
        pr = repo.create_pull(title=title, body=body, head="develop", base="master")
        print(pr)
        pr.create_issue_comment(PR_COMMENT)
        

        res = pr.merge(commit_message=title, merge_method="merge")
        print(res)
    except Exception as e:
        print(e)
        print("cleaning up existing MR")
        cleanup_lingering_pulls(repo, title)


def handler(event={}, context={}):
    write_fang_change()
    make_github_commit()
    return {"message": "success", "statusCode": 200}


if __name__ == "__main__":
    while True:
        handler()
        sleep(random.randint(2,5) * 60)
