## Tweet collecting and visualisation app

** Note: **

* DO NOT run this code in production. It was never intended to be run as a production app there are a number of limitation which would make it unwise to do so.

* This app was developed in linux and will assume it will be run on a ubuntu based environment.

* The web application (frontend) has only be tested in Chrome 55+ (whilst it may run in other browsers I have not tested it).

* You will need a Twitter API account

#### Installation

* Set a the following bash environment variables or edit core/settings.py
 - DJANGO_SECRET_KEY
 - TWITTER_CONSUMER
 - TWITTER_SECRET
 - TWITTER_ACCESS_TOKEN
 - TWITTER_ACCESS_TOKEN_SECRET
 - TWITTER_ACCOUNT    -    This must start with an @ symbol

* Create a new virtual environment (using python3) and activate it: https://virtualenv.pypa.io/en/stable/

* Pip install the requirements file:

    `pip install -r requirements.txt`

* Install the application database:

    `python manage.py migrate`

* Import the CSV country data:

    `python manage.py import-csv`

* Run the application:

    `python manage.py runserver`

* In a new console, with virtualenv enabled run the command:

    `python manage.py collect-tweets`

* Open the app in Chrome http://localhost:8000

#### Design

This application has been designed to collect tweets from the given (`settings.py:TWITTER['TWITTER_ACCOUNT']``) Twitter account and display them in the browser.

##### The CSV importer
The CSV importer will import the contents of countries.csv into the application database. Whilst importing it checks each country has a lng and lat value. If it does not we discount it (we will not be able to use null, lng, lat).

##### The collection app
The collection app `manage.py collect-tweets` polls a django app end point which will gather tweets from the API.

Upon collecting tweets it will analyse the tweet for hashtags relating to countries or country names.
If it finds a country it will map the tweet on the map.
If it does not find a country then the app will search for basic GEO data from the tweet (regarding the country the tweet came from).
If no tweet is found then the tweet will not be assigned a country value.

** Limitations **

It is highly recommended you read the limitations around this code block within the tweeting.views.get_tweets app. This code is not secure and could be open to abuse.

In the ideal world this code will be run by a celery task on the server with no outside instruction.

This code will also only look for the first instance of a country within a tweet. If multiple are found the other countries will be discounted.

This code does not do a full text search of the tweet.

#### The webapp
The web application relies on sockets to send data to the browser. By doing this we can have seamless data transfer between the browser and the server. Upon connecting to the app the browser will receive a number of tweets (if the collector has gathered results).

The latest 10 tweets will be present in the sidebar whilst tweets which contain geo or country data will be present on the map.

If new tweets are collected then the new tweets will be consumed by the browser and the results updated.
