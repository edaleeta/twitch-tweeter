"""APScheduler job functions."""

import random
from model import User, db
import twitch_helpers
import template_helpers


def fetch_twitch_data(user_id):
    """Job: Grab data about user's stream. Write it to db."""
    try:
        with db.app.app_context():
            print("Fetching stream info for {} now.".format(user_id))
            user = User.get_user_from_id(user_id)
            stream_data = twitch_helpers.serialize_twitch_stream_data(user)
            print(stream_data)
            if stream_data:
                twitch_helpers.write_twitch_stream_data(user, stream_data)
    except Exception as e:
        print(e)


def send_tweets(user_id):
    """Job: Sends a random tweet to user's Twitter account."""
    try:
        with db.app.app_context():
            user = User.get_user_from_id(user_id)
            templates = [template.contents for template in user.templates]
            random_template = random.choice(templates)

            tweet_copy = template_helpers.populate_tweet_template(
                random_template, user_id
            )
            if tweet_copy:
                template_helpers.publish_to_twitter(tweet_copy, user_id)
    except Exception as e:
        print(e)


def renew_stream_webhook(user_id):
    """Job: Renews webhook for user's stream."""
    try:
        with db.app.app_context():
            print("Renewing User {}'s webhook now.".format(user_id))
            user = User.get_user_from_id(user_id)
            twitch_helpers.subscribe_to_user_stream_events(user)
    except Exception as e:
        print(e)




if __name__ == "__main__":
    # Interact with db if we run this module directly.

    from server import app
    from model import connect_to_db
    connect_to_db(app)
    print("Connected to DB.")