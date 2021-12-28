import logging, traceback

from api import db


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


def delete_row_from_db(table, uuid):
    try:
        db.session.delete(table.query.filter_by(uuid=uuid).first())
        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False
