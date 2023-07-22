import json
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models import engine, Post, Channel

Session = sessionmaker(bind=engine)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":
    session = Session()
    channels = session.query(Channel.source_name).distinct().all()
    channel_names = [channel[0] for channel in channels]
    print(channel_names)
    for channel in channel_names:
        posts = session.query(Channel).filter(text("source_name = :channel")).params(channel=channel).all()
        data = []
        for post in posts:
            data.append({
                'id': post.id,
                'title': post.title,
                'url': post.url,
                'content': post.content,
                'popularity': post.popularity,
                'created_at': str(post.created_at),
                'updated_at': str(post.updated_at)
            })
        json_file = os.path.join(BASE_DIR, 'channels', f'{channel}.json')
        # Сохраняем данные в файл JSON
        with open(json_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
