import time
import requests
import threading

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    A management command to call the /get/tweets endpoint. By calling this end
    point the app will gather tweet information for the specific account.

    Limitation:
    * There is currently a hard coded URL. This will break if anything other
    than localhost:8000/get/tweets is called.

    * This is a self polling application, in the real world this command would
    not exist and a celery task created.
    """

    help = 'Polls localhost:8000/get/tweets for new tweets (ctrl+c to quit)'

    def poll(self, interval):
        while True:
            try:
                response = requests.get('http://localhost:8000/get/tweets')
            except requests.exceptions.ConnectionError:
                print(
                    'An error occurred, is the development server running'
                    ' on port 8000?'
                )
            else:
                if response.status_code == 200:
                    print('Successfully contacted twitter')
                else:
                    print('Something went wrong: {}'.format(response.text))
            time.sleep(interval)



    def handle(self, *args, **options):
        poll_interval = settings.TWITTER.get('POLL_INTERVAL', 10)
        print('Polling every {} seconds'.format(poll_interval))

        # We shall poll to get the data from the server.
        t = threading.Thread(target=self.poll, args=(poll_interval,))
        t.start()


        try:
            print('press ctrl+c to exit')
            t.join()
        except:
            print('finished')
