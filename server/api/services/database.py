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


def update_row_from_db(db_obj, uuid, dict_update):
    try:
        db_obj.query.filter_by(uuid=uuid).update(dict_update)
        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False


def delete_row_from_db(db_obj, uuid):
    try:
        db.session.delete(db_obj.query.filter_by(uuid=uuid).first())
        db.session.commit()
        db.session.close()
        return True

    except Exception:
        logging.error(traceback.format_exc())
        return False
