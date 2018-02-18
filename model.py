"""Models and database functions for Yet Another Twitch Toolkit."""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import desc

db = SQLAlchemy()

###############################################################################
# MODEL DEFINITIONS
###############################################################################
# TODO: Clean up static/class methods


class User(db.Model):
    """User of Yet Another Twitch Toolkit."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    twitch_displayname = db.Column(db.Text)
    twitch_username = db.Column(db.Text)
    twitch_id = db.Column(db.Text, unique=True)
    twitter_id = db.Column(db.Text)

    is_active = True
    is_authenticated = True
    is_anonymous = False

    @classmethod
    def get_user_from_id(cls, user_id):
        """Get the user object for the given id."""

        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_users_from_email(cls, user_email):
        """Find the users for the given email."""

        return cls.query.filter_by(email=user_email).all()

    @staticmethod
    def get_user_from_twitch_id(twitch_id):
        """Find the user for the given Twitch ID."""

        return User.query.filter_by(twitch_id=twitch_id).first()

    def __repr__(self):
        """Print helpful information."""

        rep = "<User user_id={}, email='{}'".format(self.user_id, self.email)
        if self.twitch_username:
            rep += ", twitch_username='{}'>".format(self.twitch_username)
            return rep
        rep += ">"
        return rep

    def update_twitch_access_token(self,
                                   access_token,
                                   refresh_token,
                                   expires_in):
        """Updates the Twitch access token and info for user."""
        my_token = self.twitch_token
        if my_token:
            my_token.access_token = access_token
            my_token.refresh_token = refresh_token
            my_token.expires_in = expires_in
        else:
            new_token = TwitchToken(
                user_id=self.user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in
            )
            db.session.add(new_token)
        db.session.commit()

    def update_twitter_access_token(self,
                                    access_token,
                                    access_token_secret):
        """Updates the Twitter access token and info for user."""
        my_token = self.twitter_token
        if my_token:
            my_token.access_token = access_token
            my_token.access_token_secret = access_token_secret
        else:
            new_token = TwitterToken(user_id=self.user_id,
                                     access_token=access_token,
                                     access_token_secret=access_token_secret)
            db.session.add(new_token)
        db.session.commit()

    def delete_template(self, template_id):
        """Allows a user to delete an owned template."""
        temp_to_del = Template.query.filter_by(template_id=template_id,
                                               user_id=self.user_id).one()
        db.session.delete(temp_to_del)
        db.session.commit()

    def edit_template(self, template_id, new_contents):
        """Allows a user to edit an owned template."""
        temp_to_edit = Template.query.filter_by(template_id=template_id,
                                                user_id=self.user_id).one()
        temp_to_edit.contents = new_contents
        db.session.commit()


class TwitchToken(db.Model):
    """Twitch access token for a user."""

    __tablename__ = "twitch_tokens"

    token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    access_token = db.Column(db.Text,
                             unique=True,
                             nullable=False)
    refresh_token = db.Column(db.Text,
                              unique=True,
                              nullable=False)
    expires_in = db.Column(db.Integer)

    user = db.relationship("User",
                           backref=backref("twitch_token", uselist=False))


class TwitterToken(db.Model):
    """Twitter access token for a user."""

    __tablename__ = "twitter_tokens"

    token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    access_token = db.Column(db.Text,
                             nullable=False)
    access_token_secret = db.Column(db.Text,
                                    nullable=False)

    user = db.relationship("User",
                           backref=backref("twitter_token", uselist=False))

    def __repr__(self):
        """Print helpful information."""

        if self.twitter_token:
            twitter_token_exists = "True"
        else:
            twitter_token_exists = "False"

        return "<AccessToken twitter_exists={}>" \
            .format(twitter_token_exists)


class Template(db.Model):
    """Template used for Tweets."""

    __tablename__ = "templates"

    template_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    contents = db.Column(db.Text, nullable=False)

    user = db.relationship("User",
                           backref=backref("templates",
                                           order_by="Template.template_id"),
                           uselist=False)

    @classmethod
    def get_template_from_id(cls, template_id):
        """Find the template for the given template_id."""

        return cls.query.filter_by(template_id=template_id).first()


class BaseTemplate(db.Model):
    """Base templates used to create templates for user upon user creation."""

    __tablename__ = "base_templates"

    template_id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """Print helpful information."""

        return "<Template template_id={}, contents='{}'>" \
            .format(self.template_id,
                    (self.contents[0:14] + "..."))


class SentTweet(db.Model):
    """Tweets created and sent."""

    __tablename__ = "sent_tweets"

    tweet_id = db.Column(db.Integer, primary_key=True)
    tweet_twtr_id = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.Text, nullable=False)
    permalink = db.Column(db.Text, nullable=False)
    clip_id = db.Column(db.Integer, db.ForeignKey("twitch_clips.clip_id"))

    user = db.relationship("User",
                           backref="sent_tweets")
    clip = db.relationship("TwitchClip", back_populates="tweet", uselist=False)

    def __repr__(self):
        """Print helpful information."""

        return "<SentTweet tweet_id='{}', user_id={}, message='{}'>" \
            .format(self.tweet_id, self.user_id, (self.message[0:14] + "..."))

    @staticmethod
    def store_sent_tweet(response, user_id, clip_id=None):
        """Saves a sent tweet in db."""
        tweet_twtr_id = response.id_str
        created_at = response.created_at
        message = response.text
        user_twtr_id = response.user.id_str
        permalink = "https://twitter.com/{}/status/{}".format(user_twtr_id,
                                                              tweet_twtr_id)
        new_sent_tweet = SentTweet(tweet_twtr_id=tweet_twtr_id,
                                   user_id=user_id,
                                   created_at=created_at,
                                   message=message,
                                   permalink=permalink,
                                   clip_id=clip_id)
        db.session.add(new_sent_tweet)
        db.session.commit()


class StreamSession(db.Model):
    """A Twitch Stream session."""

    __tablename__ = "stream_sessions"

    stream_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    twitch_session_id = db.Column(db.String(16),
                                  nullable=False,
                                  unique=True)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)

    feedback = db.relationship("StreamSessionUserFeedback",
                               back_populates="session",
                               uselist=False)
    user = db.relationship("User",
                           backref=backref("sessions",
                                           order_by="StreamSession.started_at"))

    def __repr__(self):
        """Print helpful information."""

        return "<StreamSession stream_id={}, twitch_session_id='{}',\
 started={}>".format(self.stream_id,
                     self.twitch_session_id,
                     self.started_at)

    @classmethod
    def save_stream_session(cls, user, stream_data):
        """Adds a new stream session linked to user."""

        t_session_id = stream_data["stream_id"]
        twitch_session = cls.get_session_from_twitch_session_id(t_session_id)
        if not twitch_session:
            user_id = user.user_id
            started_at = stream_data["started_at"]
            new_session = StreamSession(user_id=user_id,
                                        twitch_session_id=t_session_id,
                                        started_at=started_at)
            db.session.add(new_session)
            db.session.commit()
            twitch_session = new_session

        # Also add an entry in stream_data to store snapshot.
        StreamDatum.save_stream_data(twitch_session, stream_data)

    @classmethod
    def end_stream_session(cls, user, timestamp):
        """Update a closed steam session with the time it was found to end."""

        current_session = cls.get_user_current_session(user)
        if current_session:
            current_session.ended_at = timestamp
            db.session.commit()
        else:
            print("All sessions ended.")

    @classmethod
    def get_session_from_twitch_session_id(cls, twitch_session_id):
        """Gets the corresponding Twitch Session based on Twitch Session id."""

        return cls.query.filter_by(twitch_session_id=twitch_session_id).first()

    @classmethod
    def get_user_current_session(cls, user):
        """Get the current open session for a user."""

        most_recent_session = cls.query.filter_by(user_id=user.user_id,
                                                  ended_at=None) \
            .order_by(cls.started_at.desc()).first()
        return most_recent_session


class StreamDatum(db.Model):
    """Data gathered from Twitch when user is live."""

    __tablename__ = "stream_data"

    data_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    stream_id = db.Column(db.Integer,
                          db.ForeignKey("stream_sessions.stream_id"),
                          nullable=False)
    game_id = db.Column(db.String(50), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)
    stream_title = db.Column(db.String(140), nullable=False)
    viewer_count = db.Column(db.Integer, nullable=False)

    session = db.relationship("StreamSession",
                              backref="data")

    def __repr__(self):
        """Print helpful information."""

        return "<StreamDatum data_id={}, game_name='{}', timestamp={}>" \
            .format(self.data_id, self.game_name, self.timestamp)

    @classmethod
    def save_stream_data(cls, session, stream_data):
        """Saves stream data for user."""

        timestamp = stream_data["timestamp"]
        stream_id = session.stream_id
        game_id = stream_data["game_id"]
        game_name = stream_data["game_name"]
        stream_title = stream_data["stream_title"]
        viewer_count = stream_data["viewer_count"]

        new_data = cls(timestamp=timestamp,
                       stream_id=stream_id,
                       game_id=game_id,
                       game_name=game_name,
                       stream_title=stream_title,
                       viewer_count=viewer_count)
        db.session.add(new_data)
        db.session.commit()


class TwitchClip(db.Model):
    """Clips auto-generated for Tweets."""

    __tablename__ = "twitch_clips"

    clip_id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Text, nullable=False)
    stream_id = db.Column(db.Integer,
                          db.ForeignKey("stream_sessions.stream_id"),
                          nullable=False)

    session = db.relationship("StreamSession",
                              backref="clips")
    tweet = db.relationship("SentTweet", back_populates="clip", uselist=False)

    def __repr__(self):
        """Print helpful information."""

        return "<TwitchClip clip_id={}, slug='{}'>".format(self.clip_id,
                                                           self.slug)

    @classmethod
    def save_twitch_clip(cls, slug, user_id):
        user = User.get_user_from_id(user_id)

        # First try to get the current open session.
        current_session = StreamSession.get_user_current_session(user)
        # If one doesn't exist, fall back to most recent session.
        if current_session is None:
            last_session = user.sessions[-1]
            stream_id = last_session.stream_id
        else:
            stream_id = current_session.stream_id
        new_clip = TwitchClip(slug=slug, stream_id=stream_id)
        db.session.add(new_clip)
        db.session.commit()

        return new_clip


class StreamSessionUserFeedback(db.Model):
    """Stores user-input for stream session."""

    __tablename__ = "stream_session_user_feedback"

    feedback_id = db.Column(db.Integer,
                            primary_key=True)
    stream_id = db.Column(db.Integer,
                          db.ForeignKey("stream_sessions.stream_id"),
                          nullable=False)
    mood_rating = db.Column(db.Integer)
    notes = db.Column(db.Text)

    session = db.relationship("StreamSession",
                              back_populates="feedback",
                              uselist=False)

    def __repr__(self):
        """Print helpful information."""

        return "<StreamLogEntry feedback_id={}, stream_id={}>" \
            .format(self.feedback_id, self.stream_id)

###############################################################################
# SAMPLE DATA
###############################################################################


def sample_data():
    """Create sample data."""

    # Empty existing data
    BaseTemplate.query.delete()
    Template.query.delete()
    TwitchClip.query.delete()
    StreamDatum.query.delete()
    StreamSession.query.delete()
    SentTweet.query.delete()
    User.query.delete()
    db.session.commit()

    # Execute raw SQL to import data from csv's in respective tables.
    project_path = os.getcwd()
    fill_users = ("COPY users FROM '" + project_path + "/sql/users.csv'")
    fill_twitch_clips = ("COPY twitch_clips FROM '" +
                         project_path + "/sql/twitch_clips.csv'")
    fill_templates = ("COPY templates FROM '" +
                      project_path + "/sql/templates.csv'")
    fill_stream_sessions = ("COPY stream_sessions FROM '" +
                            project_path + "/sql/stream_sessions.csv'")
    fill_stream_data = ("COPY stream_data FROM '" +
                        project_path + "/sql/stream_data.csv'")
    fill_sent_tweets = ("COPY sent_tweets FROM '" +
                        project_path + "/sql/sent_tweets.csv'")
    fill_base_templates = ("COPY base_templates FROM '" +
                           project_path + "/sql/base_templates.csv'")

    db.session.execute(fill_base_templates)
    db.session.execute(fill_users)
    db.session.execute(fill_templates)
    db.session.execute(fill_stream_sessions)
    db.session.execute(fill_stream_data)
    db.session.execute(fill_twitch_clips)
    db.session.execute(fill_sent_tweets)
    db.session.commit()

    # Add Template entry per base template for each initial user.
    base_templates = BaseTemplate.query
    initial_users = User.query

    for user in initial_users:
        for base_template in base_templates:
            db.session.add(Template(user_id=user.user_id,
                                    contents=base_template.contents))
    db.session.commit()

###############################################################################
# HELPER FUNCTIONS
###############################################################################


def connect_to_db(app, db_uri="postgresql:///yattk", show_sql=True):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = show_sql
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
