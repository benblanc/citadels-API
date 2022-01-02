def error_handling_request():
    response = "Something went wrong while handling the request."

    return response, 500


def error_writing_database(item="row"):
    response = "Something went wrong while writing the {item} to the database.".format(item=item)

    return response, 500


def error_updating_database(item="row"):
    response = "Something went wrong while updating the {item} in the database.".format(item=item)

    return response, 500


def error_deleting_database(item="row"):
    response = "Something went wrong while deleting the {item} in the database.".format(item=item)

    return response, 500
