#!/usr/bin/env python3
import json
import lz4.block
import os
import glob
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def get_page_title(url):
    if 'about:' in url:
        return "Default Mozilla Page"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.title.string.strip() if soup.title else "No Title"
    except Exception:
        return url


def load_workspace_names():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        names_file = os.path.join(script_dir, 'workspace_names.json')
        with open(names_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load workspace names file: {e}")
        return {}


def find_firefox_session_files():
    home = str(Path.home())
    profile_path = f"{home}/Library/Application Support/zen/Profiles/"
    profile_sessions = {}

    if os.path.exists(profile_path):
        for profile_dir in glob.glob(profile_path + "*/"):
            profile_name = os.path.basename(os.path.dirname(profile_dir))
            recovery_file = os.path.join(profile_dir, "sessionstore-backups/recovery.jsonlz4")
            previous_file = os.path.join(profile_dir, "sessionstore-backups/previous.jsonlz4")

            profile_files = []
            if os.path.exists(recovery_file):
                profile_files.append(recovery_file)
            if os.path.exists(previous_file):
                profile_files.append(previous_file)

            if profile_files:
                profile_sessions[profile_name] = profile_files

    return profile_sessions


def read_session_file(session_file):
    try:
        with open(session_file, "rb") as f:
            magic = f.read(8)
            content = lz4.block.decompress(f.read())
        return json.loads(content), os.path.getmtime(session_file)
    except Exception as e:
        print(f"Error reading {session_file}: {e}")
        return None, 0


def format_url(url):
    if url.startswith('about:'):
        return "Default Mozilla Page"
    if url.startswith('moz-extension:'):
        return url
    return url.split('?')[0]


def print_workspace_summary(name, tabs_data):
    pinned = [tab for tab in tabs_data if tab['pinned']]
    regular = [tab for tab in tabs_data if not tab['pinned']]

    output = []
    output.append(f"\n## {name}")
    output.append(f"_Total Tabs: {len(tabs_data)} ({len(pinned)} pinned, {len(regular)} regular)_\n")

    if pinned:
        output.append(f"### 📌 Pinned Tabs")
        for tab in pinned:
            output.append(f"- {format_url(tab['url'])} - {get_page_title(tab['url'])}")
        output.append("")

    if regular:
        output.append(f"### 🔹 Regular Tabs")
        for tab in regular:
            output.append(f"- {format_url(tab['url'])} - {get_page_title(tab['url'])}")
        output.append("")

    return "\n".join(output)


def write_to_markdown(content, profile_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zen_workspaces_{profile_name}_{timestamp}.md"
    filepath = os.path.join(script_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Workspace summary for profile '{profile_name}' written to: {filepath}")


def main():
    # Parse command line arguments
    output_mode = "save-file"  # default
    if len(sys.argv) > 1:
        if sys.argv[1] == "log-only":
            output_mode = "log-only"
        elif sys.argv[1] != "save-file":
            print("Usage: script.py [save-file|log-only]")
            print("  save-file - write to markdown file (default)")
            print("  log-only  - output to console")
            return

    profile_sessions = find_firefox_session_files()
    if not profile_sessions:
        print("No Firefox profiles found with session files.")
        return

    WORKSPACE_NAMES = load_workspace_names()

    for profile_name, session_files in profile_sessions.items():
        latest_data = None
        latest_time = 0

        for session_file in session_files:
            data, mtime = read_session_file(session_file)
            if data and mtime > latest_time:
                latest_data = data
                latest_time = mtime

        if not latest_data:
            continue

        workspace_tabs = defaultdict(list)
        essential_tabs = []

        for window in latest_data.get('windows', []):
            for tab in window.get('tabs', []):
                entries = tab.get('entries', [])
                if entries:
                    current_index = tab.get('index', len(entries)) - 1
                    if 0 <= current_index < len(entries):
                        url = entries[current_index].get('url', '')
                        tab_info = {'url': url, 'pinned': tab.get('pinned', False)}

                        if tab.get('zenEssential', False):
                            essential_tabs.append(tab_info)
                        else:
                            workspace_id = tab.get('zenWorkspace', 'default')
                            workspace_tabs[workspace_id].append(tab_info)

        # Build output content
        output = []
        output.append("# 🌟 ZEN WORKSPACE SUMMARY")
        output.append(f"_Profile: {profile_name}_")
        output.append(f"_Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

        unnamed_workspaces = [
            workspace_id for workspace_id in workspace_tabs.keys()
            if workspace_id not in WORKSPACE_NAMES and workspace_id != 'default'
        ]

        if unnamed_workspaces:
            output.append("## ⚠️ Unnamed Workspaces")
            output.append("_The following workspaces need to be named in workspace_names.json:_\n")
            for workspace_id in unnamed_workspaces:
                output.append(f"- `{workspace_id}`")
            output.append("")

        total_workspaces = len(workspace_tabs) + (1 if essential_tabs else 0)
        total_tabs = sum(len(tabs) for tabs in workspace_tabs.values()) + len(essential_tabs)
        output.append(f"_Total Workspaces: {total_workspaces}_")
        output.append(f"_Total Tabs: {total_tabs}_\n")


        # Add essential tabs section
        if essential_tabs:
            output.append("\n## ⭐ Essential Tabs")
            output.append(f"_Total Tabs: {len(essential_tabs)}_\n")
            output.append("### 🔸 Tabs")
            for tab in essential_tabs:
                output.append(f"- {format_url(tab['url'])} - {get_page_title(tab['url'])}")
            output.append("")

        for workspace_id, tabs in workspace_tabs.items():
            workspace_name = WORKSPACE_NAMES.get(workspace_id, f"Unnamed Workspace ({workspace_id})")
            output.append(print_workspace_summary(workspace_name, tabs))

        content = "\n".join(output)
        if output_mode == "save-file":
            write_to_markdown(content, profile_name)
        else:
            print(content)

if __name__ == "__main__":
    main()