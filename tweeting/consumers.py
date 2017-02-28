import simplejson

from channels import Group
from channels.handler import AsgiHandler
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Tweet


def tweet_response(tweets):
    """
    Helper: returns tweet results to clients
    """
    tweets = reversed(Tweet.objects.order_by('-id')[:tweets])
    response_objects = list(map(lambda x: x.serialized_data(), tweets))

    Group('tweety').send({
        'text': simplejson.dumps(response_objects)
    })


@receiver(post_save, sender=Tweet)
def update_tweet_channel(sender, instance, **kwargs):
    """
    Post save hook, when a tweet is saved replay the latest 10 tweets to the
    active clients.
    """
    tweet_response(settings.TWITTER.get('RESULT_COUNT', 10))


def webservice_add(message):
    """
    When joining the channel the client will be sent results in response.
    """
    message.reply_channel.send({'accept': True})
    Group('tweety').add(message.reply_channel)

    tweet_response(settings.TWITTER.get('RESULT_COUNT', 10))


def webservice_disconnect(message):
    """
    On disconnection discard the response channel
    """
    Group('tweety').discard(message.reply_channel)
