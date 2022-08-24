from os import environ
ENVIRONMENT = environ.get('ENVIRONMENT', 'development')
DOMAIN = environ.get('DOMAIN', 'duocheng')


def name_formatter(domain=DOMAIN, environment=ENVIRONMENT, version='1', *, typ: str, name: str):
    """
    生成 topic 的名称
    """
    return f'{domain}.{environment}.{typ}.{name}.{version}'
