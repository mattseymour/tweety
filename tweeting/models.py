from django.db import models


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
