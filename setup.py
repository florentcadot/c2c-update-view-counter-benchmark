from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from main import DB
import logging

log = logging.getLogger(__name__)

def setup():
    """
        Create column view_count with default value set to 0 in documents table
    """
    engine = create_engine(DB, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    sql_query = text("""
        ALTER TABLE guidebook.documents
        ADD COLUMN view_count INTEGER DEFAULT 0;
    """)
    session.execute(sql_query)
    session.commit()

if __name__ == '__main__':
    log.info(f'Creating column view_count with default value set to 0 in documents table...')
    setup()
    log.info(f'Done!')



