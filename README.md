# LichessAutoFiller

## Installation
1. Git clone this repo
2. (optional) Create venv using ```python -m venv venv``` and activate: ```source venv/bin/activate```
3. Install all requirements: ```python -m pip install -r requirements.txt```
4. Copy env example file ```cp .env.example .env``` and env variables

## Usage
+ Run ```python app/main.py -d=<current-date>``` to fill admin.itmo for specified date.
  Students fio are loading from google sheet, linked by lichess nick from file.

## Plans
+ full automatisation: move lichess stats code here

## Contributions
Contributions to the code are always welcome,
pool requests will be checked and merged to main branch
