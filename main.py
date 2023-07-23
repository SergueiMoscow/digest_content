import json
import os

from fastapi import FastAPI
from sqlalchemy import not_, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from digest_settings import days_before, min_post_popularity
from models import Subscription, Digest, Post, engine

app = FastAPI()
Session = sessionmaker(bind=engine)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/digest")
def create_digest(user_id: int):
    posts_for_digest = get_posts_for_digest(user_id)
    if len(posts_for_digest) == 0:
        return None
    save_digest(user_id, posts_for_digest)
    return json.dumps(posts_for_digest, ensure_ascii=False, indent=4)


def get_posts_for_digest(user_id: int) -> list:
    """
    search for posts in channels,
    :param user_id:
    :return: list of post dicts
    """
    session = Session()
    rows_subscriptions = session.query(Subscription.source_name).filter(Subscription.user_id == user_id).all()
    subscriptions = [v[0] for v in rows_subscriptions]
    min_post_time = datetime.utcnow() - timedelta(days=days_before)
    posts_for_digest = []
    last_sent_post_ids = get_last_sent_post_ids(user_id)
    for subscription in subscriptions:
        source = os.path.join(BASE_DIR, 'channels', f'{subscription}.json')
        with open(source) as f:
            posts = json.load(f)
            if posts is None:
                return []
        for post in posts:
            if post['popularity'] < min_post_popularity:
                continue
            if datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S.%f') < min_post_time:
                continue
            post_for_digest = session.query(Post)\
                .filter(text('source_name = :subscription'), text("source_id = :id"))\
                .params(subscription=subscription, id=post['id'])\
                .first()
            if post_for_digest is not None:
                if post_for_digest.id in last_sent_post_ids:
                    continue
            else:
                post_for_digest = Post(
                    source_id=post['id'],
                    source_name=subscription,
                    title=post['title'],
                    content=post['content'],
                    popularity=post['popularity'],
                    url=post['url'],
                    created_at=post['created_at']
                )
                session.add(post_for_digest)
                session.commit()
            post_dict = {
                'id': post_for_digest.id,
                'source_name': post_for_digest.source_name,
                'source_id': post_for_digest.source_id,
                'title': post_for_digest.title,
                'content': post_for_digest.content,
                'popularity': post_for_digest.popularity,
                'url': post_for_digest.url,
                'created_at': post_for_digest.created_at.isoformat(),
            }
            posts_for_digest.append(post_dict)
    session.close()
    return posts_for_digest


def get_last_sent_post_ids(user_id: int) -> list:
    """
    search for last ids of posts (from digest) sent to user
    :param user_id:
    :return: last post ids sent to user
    """
    session = Session()
    min_post_time = datetime.utcnow() - timedelta(days=days_before)

    last_digests = session.query(Digest.post_ids)\
        .filter(
            text('user_id = :user_id'),
            Digest.created_at > min_post_time
        )\
        .params(user_id=user_id).\
        all()
    ids = [p_id for p_ids in last_digests for p_id in p_ids[0]]
    return ids


def save_digest(user_id: int, posts: list) -> None:
    """
    saves ids of posts for this digest
    :param user_id:
    :param posts:
    :return:
    """
    session = Session()
    post_ids = [post['id'] for post in posts]
    new_digest = Digest(user_id=user_id, post_ids=post_ids)
    session.add(new_digest)
    session.commit()
    session.close()


if __name__ == '__main__':
    digest = create_digest(2)
    print(digest)
