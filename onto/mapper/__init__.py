import warnings

try:
    import marshmallow.validate as validate
except ImportError:
    warnings.warn("marshmallow.validate not imported as onto.mapper.validate")
