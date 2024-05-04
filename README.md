# ENTSOE scraper

This ongoing project is intended for getting open-source electricity market data in Europe, published
by [ENTSOE Transparency Platform](https://transparency.entsoe.eu/dashboard/show) with emphasis on day-ahead and
intraday markets. Currently, the default horizon is set to 1 week ahead of present day.

## Before you start

### 1. Get API key

In order to access the data, you need personalized API
key. [Here](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_authentication_and_authorisation)
you will fid out how to receive your key. Once accessed, please create credentials.json file in bin/ and
paste your key:

    {
        "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }

### 2. Check the initial configuration

Currently, configuration is stored in bin/config/Config.py file that includes:

- local timezone (change if needed)
- data server timezone (constant)
- default start/end time for initializing database and validating dataset (change if needed)
- T-SQL server name (change if needed)
- T-SQL db name (change if needed)
- T-SQL db link (change if needed)

### 3. Create virtual environment

See [here](https://docs.python.org/3/library/venv.html) how to create
and [here](https://docs.python.org/3/tutorial/venv.html) how to activate it.

### 4. Install the necessary packages

In your terminal type:

    pip install requirements.txt

## Initializing/validating data

First, the application maps all necessary items (i.e. bid zones, datetimes, holidays, countries etc.) and saves/updates them in
the db. It may take considerable amount of time.