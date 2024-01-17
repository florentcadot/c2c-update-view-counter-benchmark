from sqlalchemy import create_engine, text, event
from queues_service import get_queue_config, publish, consume_all_messages
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from collections import Counter
import math
import time
import sys
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DB='postgresql://www-data:www-data@localhost:5432/c2corg'

# The max number of documents to update per transaction
MAX_REQ = 4000

# The number of seconds to wait between each transaction
SLEEP_TIME = 2

# Bulk update base statement
BASE_STMT = """
    UPDATE guidebook.documents
    SET view_count = documents.view_count + updates.view_count
    FROM (VALUES
        {stmt_values}
        ) AS updates(document_id, view_count)
    WHERE documents.document_id = updates.document_id;
"""


def increment_documents_views():
    queue_config = get_queue_config()

    def process_task(doc_ids):
        engine = create_engine(DB, echo=False)
        # KEEP EVEN IF NOT USED: event listeners are automatically registered when importing
        from query_profiling import before_cursor_execute, after_cursor_execute
        Session = sessionmaker(bind=engine)
        session = Session()

        if len(doc_ids) != 0:
            doc_views = list(Counter(doc_ids).items())
            max_iteration = math.ceil(len(doc_views) / MAX_REQ)
            for i in range(max_iteration):
                docs = []
                for id, count in doc_views[i * MAX_REQ:(i + 1) * MAX_REQ]:
                    docs.append({
                     'document_id': id,
                     'view_count': count
                    })
                stmt_values = ", ".join(
                 f"({doc['document_id']}, {doc['view_count']})"
                 for doc in docs
                )
                stmt = text(BASE_STMT.format(stmt_values=stmt_values))
                session.execute(stmt)
                session.commit()
                docs.clear()
                if max_iteration > 1 and i != max_iteration - 1:
                    # Sleep to prevent blocking other transactions
                    time.sleep(SLEEP_TIME)

    consume_all_messages(queue_config, process_task)


def init(docs_amount):
    """
        Get docs_amount docs from the database and push their ids to the redis queue
    """
    engine = create_engine(DB, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    query = text("SELECT document_id FROM guidebook.documents LIMIT :limit")
    query = query.bindparams(limit=docs_amount)
    result = session.execute(query)
    session.commit()

    rows = result.fetchall()
    documents_views_queue_config = get_queue_config()
    for row in rows:
        publish(documents_views_queue_config, row.document_id)


if __name__ == '__main__':
    docs_amount = sys.argv[1:][0]
    log.info(f'Initialization: pushing {docs_amount} docs ids to the Redis queue....')
    init(docs_amount)

    log.info(f'Let\'s go: Updating documents view counters....')
    increment_documents_views()