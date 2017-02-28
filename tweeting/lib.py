
from django.db.models import Q

from .models import Tweet, Country

def process_tweet(tweet):
    """
    Processes information found within the tweet, currently used to look at
    hash tags and other geolocation information.

    Limitation:
    * Really inefficient, this code currently does an SQL query per hashtag
    * Does not do full text searching
    """
    location = None
    country = None

    tweet_object = Tweet(
        uid=tweet.id_str,
        text=tweet.text
    )

    countries = Country.objects.all().values('id', 'country_code')

    # this is really intesive and inefficient it should be changed (future)
    def hash_country(tag):
        """
        For each hash tag we shall query the database to see if the tag is also
        a country. Where this is the case we shall set a country to the tweet.
        """
        tag = tag.text
        _country = None
        for iter_country in countries:
            matching_country = Country.objects.filter(
                Q(country_code=tag.upper()) | Q(country=tag.lower())
            ).first()
            if matching_country:
                return matching_country
        return None

    __country = map(hash_country, tweet.hashtags)
    country_hashtag = list(filter(lambda x: x is not None, __country))
    # try to get the location from the text first
    # failing that we shall fall back to the country
    # if the country is not present then no location will be included.
    if country_hashtag:
        tweet_object.country = country_hashtag[0]
    elif tweet.coordinates:
        _long, _lat = tweet.coordinates.get('coordinates', )
        tweet_object.lng, tweet_object.lat = _long, _lat
    elif tweet.place:
        _country_code = tweet.place.get('country_code');
        try:
            country = Country.objects.get(
                country_code=_country_code.upper()
            )
            tweet_object.country = country
        except Country.DoesNotExist:
            # if we cannot find a location then there is no point
            # putting it on the map.
            pass

    try:
        Tweet.objects.get(uid=tweet.id_str)
    except Tweet.DoesNotExist:
        tweet_object.save()
