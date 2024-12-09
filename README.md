# Zen Browser Workspace Catalog

A Python utility to generate a Markdown catalog of your Zen Browser workspaces and tabs across multiple profiles.

## Features

- Lists all workspaces and tabs across multiple profiles
- Categorizes tabs (Essential, Pinned, Regular)
- Identifies unnamed workspaces
- Generates timestamped Markdown reports per profile
- Configurable workspace names
- Fetches page titles for tabs
- Supports console output or file saving

## Requirements

- Python 3.6+
- lz4
- requests
- beautifulsoup4
- Zen Browser installed

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd zen-workspace-catalog
```

2. Install required packages:
```bash
pip install lz4 requests beautifulsoup4
```

3. Copy `workspace_names.json.example` to `workspace_names.json` and customize your workspace names:
```bash
cp workspace_names.json.example workspace_names.json
```

## Usage

Run the script with one of these options:
```bash
# Save to markdown files (default)
python3 main.py
# or explicitly
python3 main.py save-file

# Output to console
python3 main.py log-only
```

When saving to files, the generated reports will be in the script directory with format:
```
zen_workspaces_[profile-name]_YYYYMMDD_HHMMSS.md
```

## Workspace Configuration

Edit `workspace_names.json` to name your workspaces:

```json
{
    "workspace-uuid": "🎨 Design Tools",
    "another-uuid": "💻 Development"
}
```

## Output Format

The generated Markdown includes:
- Profile name
- Timestamp of generation
- List of unnamed workspaces
- Total workspace and tab counts
- Essential tabs section (if present)
- Individual workspace sections with:
  - Pinned tabs with page titles
  - Regular tabs with page titles

Example output structure:
```markdown
# 🌟 ZEN WORKSPACE SUMMARY
_Profile: Default_
_Generated on: 2024-01-01 12:34:56_

## ⚠️ Unnamed Workspaces
_The following workspaces need to be named in workspace_names.json:_
- `workspace-uuid-123`

_Total Workspaces: 5_
_Total Tabs: 25_

## ⭐ Essential Tabs
_Total Tabs: 3_
### 🔸 Tabs
- tab1.com - Tab 1 Title
- tab2.com - Tab 2 Title

## 🎨 Design Tools
_Total Tabs: 4 (1 pinned, 3 regular)_

### 📌 Pinned Tabs
- pintab.com - Pinned Tab Title

### 🔹 Regular Tabs
- tab3.com - Regular Tab Title
```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

MIT License
```

This update includes:
1. Multiple profile support
2. New command-line arguments
3. Page title fetching feature
4. Updated requirements
5. More detailed output format example
6. Clearer usage instructions