from sqlalchemy import Column, String, Integer

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Vacancies(Base):

    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    spider = Column(String, nullable=True)
    url = Column(String, nullable=True)
    name = Column(String, nullable=True)
    employer = Column(String, nullable=True)
    salary = Column(String, nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.spider = kwargs.get('spider')
        self.url = kwargs.get('url')
        self.employer = kwargs.get('employer')
        self.salary = kwargs.get('salary')
