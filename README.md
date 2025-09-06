# LichessAutoFiller

## Installation
1. Git clone this repo
2. (optional) Create venv using ```python -m venv venv``` and activate: ```source venv/bin/activate```
3. Install all requirements: ```python -m pip install -r requirements.txt```
4. Copy env example file ```cp .env.example .env``` and fill path to file with lichess nicks & path to credentials.json

## Usage
```bash
python app/main.py \
  --date=<current-date> \
  --tournament_id=<tournament id of lesson> \
  --required_practice_time=<min lesson time (usually 45)> \
  --lection_time=<lection time (usually 30 )> \
  --update_sheets=<1 if should update google sheets> \
  --fill_visitings=<1 if should update isu admin>
```

Students fio are loading from google sheet, linked by lichess nicks from lichess api.

## Plans
- [x] full automatisation: move lichess stats code here
- [ ] link students by ISU id & fill google sheets with ISU ID
- [ ] refactor lesson participation logic + improve it

## Contributions
Contributions to the code are always welcome,
pool requests will be checked and merged to main branch
