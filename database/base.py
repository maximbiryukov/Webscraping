from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base


class VacanciesDB:

    def __init__(self, url):
        self.url = url

    def add_row(self, db_item):

        self.engine = create_engine(self.url)
        Base.metadata.create_all(self.engine)
        db_session = sessionmaker(bind=self.engine)

        session = db_session()
        session.add(db_item)
        session.commit()
        session.close()




