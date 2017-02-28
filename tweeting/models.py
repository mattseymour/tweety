from django.db import models
from django.conf import settings


class Country(models.Model):
    """
    Holds content from the countries.csv file, putting this into a model will
    make querying easier and more efficient.
    """
    country = models.CharField(max_length=200)
    # fields below are nullable incase there is any bad data during import
    country_code = models.CharField(max_length=10, null=True, blank=True)
    lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    def __str__(self):
        return self.country

    def getLngLat(self):
        return (self.lng, self.lat,)

    def save(self, *args, **kwargs):
        # lets standardise the input at this point
        # just means we can be a little quicker with development
        self.country_code = self.country_coe.upper()
        self.country = self.country.lower()

        super(self, Country).save(*args, **kwargs)


class AccountManager(models.Manager):

    def get_queryset(self):
        # we will only return tweets from the currently active twitter account
        return super(AccountManager, self).get_queryset().filter(
            account=settings.TWITTER['ACCOUNT']
        )


class Tweet(models.Model):
    """
    Holds simple tweet data for the app.
    """
    account = models.CharField(max_length=140, blank=True)
    uid = models.CharField(unique=True, max_length=20)
    text = models.CharField(max_length=140)
    country = models.ForeignKey('Country', null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Override the default manager so we do not get the wrong accounts
    # tweets if someone changes settings
    objects = AccountManager()

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        # Make sure we capture which account the tweet is from
        self.account = settings.TWITTER['ACCOUNT']
        super(Tweet, self).save(*args, **kwargs)

    def serialized_data(self):
        """
        Crude serializer so we can return the model in a serialized way.
        """

        lat = self.lat
        lng = self.lng

        if self.country:
            lat = self.country.lat
            lng = self.country.lng

        return{
            'account': self.account,
            'uid': self.uid,
            'text': self.text,
            'lat': lat,
            'lng': lng
        }
