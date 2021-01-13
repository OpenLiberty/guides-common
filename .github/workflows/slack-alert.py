import requests
import json
from argparse import ArgumentParser

message = {
    "attachments": [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Daily Build"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Status:*\n FAILURE"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Dev Date:*\n 2020-"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Build Level:*\nAll vowel keys aren't working."
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Driver Location:* blabla"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*<fakeLink.toEmployeeProfile.com| Builds>*"
                    }
                }
            ]
        }
    ]
}

headers = {
    "Content-type": "application/json"
}

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('buildlevel', type=str)
    parser.add_argument('driverlocation', type=str)
    parser.add_argument('devdate', type=str)
    parser.add_argument('status', type=str)
    parser.add_argument('ownerRepo', type=str)
    parser.add_argument('runID', type=str)
    parser.add_argument('slackhook', type=str)
    args = parser.parse_args()

    message["attachments"][0]["blocks"][1]["fields"][
        0]["text"] = f"*Status:*\n {args.status}"
    message["attachments"][0]["blocks"][1]["fields"][
        1]["text"] = f"*Dev Date:*\n {args.devdate}"
    message["attachments"][0]["blocks"][1]["fields"][2][
        "text"] = f"*Build Level:*\n {args.buildlevel}"
    message["attachments"][0]["blocks"][2]["text"][
        "text"] = f"*Driver Location:* {args.driverlocation}"
    workflow_url = f"https://github.com/{args.ownerRepo}/actions/runs/{args.runID}"
    message["attachments"][0]["blocks"][3]["text"]["text"] = f"*<{workflow_url}| Builds>*"

    status = args.status
    if status == 'failure':
        message["attachments"][0]["color"] = "#d73a49"
    elif status == 'success':
        message["attachments"][0]["color"] = "#28a745"
    else:
        message["attachments"][0]["color"] = "#f6f8fa"

    requests.post(args.slackhook, headers=headers, data=json.dumps(message))
