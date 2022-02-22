import logging, traceback

from api import db

from pprint import pprint


def write_row_to_db(row):
    try:
        db.session.add(row)
        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False


def update_row_in_db(table, uuid, dict_update):
    try:
        table.query.filter_by(uuid=uuid).update(dict_update)
        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False


def delete_row_from_db_where(table, **kwargs):
    try:
        row = table.query.filter_by(**kwargs).first()

        if row:
            db.session.delete(row)
            db.session.commit()
            db.session.close()

        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False


def delete_row_from_db(table, uuid):
    return delete_row_from_db_where(table, uuid=uuid)


def delete_rows_from_db(table, **kwargs):
    try:
        rows = table.query.filter_by(**kwargs).all()

        for row in rows:
            db.session.delete(row)

        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False
