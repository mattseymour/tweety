import json
import twitter

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from .models import Tweet
from .lib import process_tweet

# VIEW: /
# Main tweeting app entry point
def index(response):
    """
    Simple renders the index.html, we get tweet information from the webservice
    """
    return render(
        response,
        'index.html',
        {
            'account': settings.TWITTER.get('ACCOUNT')
        }
    )


# VIEW: /get/tweets/
# Returns 200 or 418 (errors)
def get_tweets(response):
    """
    Gets the tweets from the defined twitter account and put them in the
    database.

    Limitation:
    * There is no function to currently delete the messages from the database.
    * This endpoing should be turned into celery task
    that will allow periodic running.
    * this will not back fill upto 10 tweets. You will need to keep the app
    runinng and wait for the user to produce 10 tweets with suitable geo data

    * SECURITY:: This endpoint has zero authentication around it. This means any
    person can access /get/tweets causing the server to perform a highly
    intensive task. This is a prime candidate for DOS of the server this app is
    running on. YOU HAVE BEEN WARNED!
    """
    try:
        api = twitter.Api(
            consumer_key=settings.TWITTER['CONSUMER_KEY'],
            consumer_secret=settings.TWITTER['CONSUMER_SECRET'],
            access_token_key=settings.TWITTER['ACCESS_TOKEN'],
            access_token_secret=settings.TWITTER['ACCESS_TOKEN_SECRET']
        )

        api.VerifyCredentials()
    except Exception:
        return HttpResponse(
            json.dumps({'message': 'Authentication error, check API keys'}),
            status=418,
            content_type='application/json'
        )

    # find the newest tweet and get its twitter id. We can use this to limit
    # results from the API and reduce finding duplicates
    max_tweet = Tweet.objects.all().order_by('-id').first()
    if max_tweet:
        # if the conditions are not met we will try and get more data
        latest_tweets = api.GetUserTimeline(
            screen_name=settings.TWITTER['ACCOUNT'],
            count=settings.TWITTER.get('RESULT_COUNT', 10),
            since_id=max_tweet.uid
        )
    else:
        latest_tweets = api.GetUserTimeline(
            screen_name=settings.TWITTER['ACCOUNT'],
            count=settings.TWITTER.get('RESULT_COUNT', 10),
        )

    errs = []
    for tweet in latest_tweets:
        try:
            process_tweet(tweet)
        except Exception as err:
            # not a pretty error but it will be good enough
            errs.append(str(err))

    if errs:
        # if something goes wrong just spill output for the time being
        return HttpResponse(
            json.dumps(errs), status=418, content_type='application/json'
        )
    return HttpResponse(status=200)
