# Installation

## Requirements

- Python 3.9 or higher
- Chrome browser (for automation)
- Internet connection

## Install from PyPI

```bash
pip install ita-scrapper
```

## Install from Source

For development or latest features:

```bash
git clone https://github.com/problemxl/ita-scrapper
cd ita-scrapper
uv pip install -e ".[dev]"
```

## Verify Installation

```python
from ita_scrapper import ITAScrapper

# Test basic functionality
scrapper = ITAScrapper()
print("✅ ITA Scrapper installed successfully!")
```

## Chrome Setup

The scrapper requires Chrome for browser automation. It will automatically download ChromeDriver if needed.

### Manual Chrome Installation

**Ubuntu/Debian:**
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download from [chrome.google.com](https://www.google.com/chrome/)

## Troubleshooting

If you encounter issues, see the [Troubleshooting Guide](../troubleshooting.md).