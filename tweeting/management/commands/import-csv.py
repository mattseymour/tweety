import os
import csv

from django.core.management.base import BaseCommand, CommandError

from ...models import Country

class Command(BaseCommand):
    help = 'Loads country csv file into database '
    '(this does a clear and load, old data will be lost) '
    'the countries.csv file must be in project root.'


    def handle(self, *args, **options):
        path = os.path.join('countries.csv')
        if os.path.exists(path):
            Country.objects.all().delete()

            country_list = []
            with open(path, 'r') as csv_fh:
                country_reader = csv.reader(csv_fh, delimiter=',')
                next(country_reader, None) # ignore the header in the file
                # Generate a list of countrys first, we will bulk insert after
                for row in country_reader:
                    # if a country does not have a lng or lat ignore it.
                    if row[2].upper() == 'NONE' or row[3].upper() == 'NONE':
                        print(
                            'Ignoring {} it has no lng or lat values, '
                            'we cannot put this on the map.'.format(
                                row[0]
                            )
                        )
                        continue
                    # add the counties to a list we will bulk import later
                    country_list.append(
                        Country(
                            country=row[0].lower(),
                            country_code=row[1].upper(),
                            lng=float(row[2]),
                            lat=float(row[3])
                        )
                    )
                # import the data
                Country.objects.bulk_create(country_list)
        else:
            raise CommandError(
                'Cannot find country.csv, make sure this file is in project root'
            )
