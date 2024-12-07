# Web-Scrapping-API

Virtual Environment Set Up

```
python -m venv venv
```
Virtual Activation[Linux]

```
source venv/bin/activate
```
Virtual Activation With Git Bash[Windows]

```
source venv/scripts/activate
```
Install Files

```
pip install -r requirements.txt
```
Migrate

```
python manage.py migrate
```

Migrations

```
python manage.py makemigrations
```

Run Project

```
python manage.py runserver
```

++++++++++++++++++++ API ++++++++++++++++++++++++

Scrape Endpoint:
URL: POST /api/scrape/
```
http://127.0.0.1:8000/api/scrape/
```

```
{
    "url": "https://theicthub.com/"
}
```

Search Endpoint:
URL: POST /api/search/
```
http://127.0.0.1:8000/api/search/
```

```
{
    "query": "Address in theicthub?",
}
```