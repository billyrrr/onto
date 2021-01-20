def validate_string(s):
    if not isinstance(s, str):
        from marshmallow import ValidationError
        raise ValidationError
