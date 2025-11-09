"""Alerting integrations."""
from __future__ import annotations

import pandas as pd
from slack_sdk.webhook import WebhookClient


def post_slack_digest(webhook_url: str, candidates: pd.DataFrame) -> None:
    """Send a formatted Slack message summarizing top candidates."""

    if candidates.empty:
        return
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Stock Scout Weekly Picks*",
            },
        },
        {"type": "divider"},
    ]
    for _, row in candidates.iterrows():
        text = (
            f"*{row.name}* | Score: {row['composite']:.1f}\n"
            f"Entry: {row['entry']:.2f} | SL: {row['stop_loss']:.2f}\n"
            f"Targets: {row['target1']:.2f} / {row['target2']:.2f}"
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    client = WebhookClient(webhook_url)
    client.send(blocks=blocks)


def dataframe_to_gsheet(df: pd.DataFrame, sheet_name: str, worksheet: str, credentials_json: str) -> None:
    """Upload dataframe to Google Sheet."""

    import gspread
    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_file(credentials_json, scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ])
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet)
    sheet.clear()
    sheet.update([df.columns.tolist()] + df.values.tolist())


def export_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)


def notify(outputs: dict, candidates: pd.DataFrame) -> None:
    """Dispatch alerts to configured channels."""

    if not outputs:
        return

    if slack_cfg := outputs.get("slack"):
        webhook = slack_cfg.get("webhook")
        if webhook:
            post_slack_digest(webhook, candidates)

    if sheet_cfg := outputs.get("google_sheet"):
        creds = sheet_cfg.get("credentials_json")
        sheet_name = sheet_cfg.get("sheet_name")
        worksheet = sheet_cfg.get("worksheet", "Weekly Picks")
        if creds and sheet_name:
            dataframe_to_gsheet(candidates.reset_index(), sheet_name, worksheet, creds)

    if archive_cfg := outputs.get("csv_archive"):
        path = archive_cfg.get("path", "data/archive/latest.csv")
        export_csv(candidates.reset_index(), path)
