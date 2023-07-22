import json

from fastapi import FastAPI
from sqlalchemy import not_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from digest_settings import days_before, min_post_popularity
from models import Subscription, Digest, Post, engine

app = FastAPI()
Session = sessionmaker(bind=engine)


@app.get("/digest")
def create_digest(user_id: int):
    posts_for_digest = get_posts_for_digest(user_id)
    if len(posts_for_digest) == 0:
        return None
    save_digest(user_id, posts_for_digest)
    return json.dumps(posts_for_digest)


def get_posts_for_digest(user_id: int):
    session = Session()
    subscriptions = session.query(Subscription.source_name).filter(Subscription.user_id == user_id).all()
    field_names = ['id', 'source_name', 'title', 'content', 'url', 'created_at']
    min_post_time = datetime.utcnow() - timedelta(days=days_before)
    digest_post_ids = [row.post_ids for row in session.query(Digest.post_ids).filter_by(user_id=user_id).all()]
    flat_digest_post_ids = [pid for pids in digest_post_ids for pid in pids]
    digest = session.query(Post.id, Post.source_name, Post.title, Post.content, Post.url, Post.created_at).filter(
            Post.source_name.in_([s[0] for s in subscriptions]),
            Post.created_at >= min_post_time,
            Post.popularity >= min_post_popularity,
            not_(Post.id.in_(flat_digest_post_ids))
        ).all()
    digest_dict = [
        {
            field: value.isoformat() if isinstance(value, datetime) else value
            for field, value in zip(field_names, row)
        }
        for row in digest
    ]
    # session.commit()
    session.close()
    return digest_dict


def save_digest(user_id, posts):
    Session = sessionmaker(bind=engine)
    session = Session()
    post_ids = [post.get("id") for post in posts]
    new_digest = Digest(user_id=user_id, post_ids=post_ids)
    session.add(new_digest)
    session.commit()
    session.close()


if __name__ == '__main__':
    digest = create_digest(3)
    print(digest)
