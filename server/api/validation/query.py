def validate_sort_order(sort_order):
    valid = False
    options = ['asc', 'desc']

    if sort_order in options:
        valid = True

    return valid


def validate_order_by(order_by, options):
    valid = False

    if order_by in options:
        valid = True

    return valid


def validate_limit(limit):
    valid = False

    if limit > 0:
        valid = True

    return valid


def validate_offset(offset):
    valid = False

    if offset >= 0:
        valid = True

    return valid


def validate_query(sort_order, order_by, limit, offset, options_order_by):
    invalid_query = None

    if sort_order:  # check if not none
        if not validate_sort_order(sort_order):
            invalid_query = 'sort_order'

    if order_by:  # check if not none
        if not validate_order_by(order_by, options_order_by):
            invalid_query = 'order_by'

    if limit:  # check if not none
        if not validate_limit(limit):
            invalid_query = 'limit'

    if offset:  # check if not none
        if not validate_offset(offset):
            invalid_query = 'offset'

    return invalid_query
