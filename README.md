# 📊 Market Actu

[![Daily Update](https://github.com/Nizar-Bd/market-actu/actions/workflows/main.yml/badge.svg)](https://github.com/Nizar-Bd/market-actu/actions/workflows/main.yml)
[![Live Demo](https://img.shields.io/badge/demo-GitHub%20Pages-blue?style=flat-square&logo=github)](https://nizar-bd.github.io/market-actu/)

Automated data pipeline that scrapes, analyzes, and archives global market summaries daily at 12:00 PM CET.

## ⚡ How it works
- **Scrape:** Extracts market data (Indices, Commodities) from Trading Economics using `curl_cffi` to bypass TLS fingerprinting.
- **Analyze:** Calculates 24h price variations by comparing current values with previous data stored in GitHub Artifacts.
- **Archive:** Generates a responsive HTML report (Pico.css) and stores a dated copy in `/archives`.
- **Deploy:** Automatically updates the live dashboard via GitHub Pages.

## 🛠️ Tech Stack
- **Core:** Python 3.9, BeautifulSoup4
- **Automation:** GitHub Actions (CRON)
- **Persistence:** JSON & GitHub Artifacts (Stateless memory)
- **Frontend:** HTML5, Pico.css (Classless CSS)

## 📂 Structure
- `newsletter_generator.py`: Main scraper & generator.
- `index.html`: Live dashboard.
- `archives/`: Daily historical reports.
- `.github/workflows/`: Automation logic.

## 🔧 Quick Start
```bash
git clone [https://github.com/Nizar-Bd/market-actu.git](https://github.com/Nizar-Bd/market-actu.git)
pip install -r requirements.txt
python newsletter_generator.py
