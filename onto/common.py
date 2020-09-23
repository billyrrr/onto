class _NA:
    """
    Used when the value of a parameter is not supplied by
        the user. Created in order to differentiate from
        None or False.

    """
    pass


def read_obj_type(d, obj_cls):
    """ Returns obj_type from the raw dictionary

    Note: "obj_type" is NOT the "attribute" property of obj_type field instance
    :param d:
    :param obj_cls:
    :return:
    """
    schema_obj = obj_cls.get_schema_obj()
    if schema_obj is None:
        if "obj_type" in d:
            return d["obj_type"]
        else:
            return None
    else:
        fds = schema_obj.fields
        if "obj_type" in fds:
            return fds["obj_type"].read_obj_type_str(d)
        else:
            return None
