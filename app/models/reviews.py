import datetime

from sqlalchemy import Column, ForeignKey, Integer, Boolean, Text, Date, SmallInteger
from sqlalchemy.orm import relationship
from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(Text)
    comment_date = Column(Date, default=datetime.date.today)
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('ratings.id'))

    rating = relationship('Rating', back_populates='review')


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(SmallInteger, nullable=True)
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))

    review = relationship('Review', back_populates='rating')
