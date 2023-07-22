import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, create_engine, ARRAY, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()
str_engine = f"postgresql://{os.getenv('pgsql_user')}:{os.getenv('pgsql_password')}@" \
             f"{os.getenv('pgsql_host')}/{os.getenv('pgsql_database')}"
engine = create_engine(str_engine)
Base = declarative_base()


class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    source_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    popularity = Column(Integer, nullable=False, server_default='0')
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    subscriptions = relationship("Subscription", back_populates="user")
    digests = relationship("Digest", back_populates="user")


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, nullable=False)
    source_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    popularity = Column(Integer, nullable=False, server_default='0')
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)

    def save(self):
        _session = sessionmaker(engine)
        session = _session()
        session.add(self)
        new_id = session.flush()
        session.commit()
        session.close()
        return self


class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    source_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="subscriptions")
    created_at = Column(DateTime, server_default=func.now(), index=True)


class Digest(Base):
    __tablename__ = 'digest'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="digests")
    post_ids = Column(ARRAY(Integer), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
