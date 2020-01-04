import pytest

from examples.fluttergram import domain_models


@pytest.fixture
def users(request, CTX):
    tijuana = domain_models.User.new(doc_id="tijuana")
    tijuana.followers = {"thomasina": True, }
    tijuana.save()

    thomasina = domain_models.User.new(doc_id="thomasina")
    thomasina.followers = dict()
    thomasina.save()

    def fin():
        tijuana.delete()
        thomasina.delete()

    request.addfinalizer(fin)

    return [tijuana, thomasina]


@pytest.fixture
def posts(users, request, CTX):
    p = domain_models.Post.new(doc_id="tj_t", owner_id="tijuana", _remainder={
        "hello": "world"
    })
    p.save()

    def fin():
        p.delete()

    request.addfinalizer(fin)

    return [p]
