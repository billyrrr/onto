def test_init():

    from onto.store import Store, reference

    from onto.domain_model import DomainModel
    from onto import attrs

    class U(DomainModel):
        class Meta:
            collection_name = "U"

        t = attrs.bproperty()

    class V(DomainModel):
        class Meta:
            collection_name = "V"

        t = attrs.bproperty()

    class UvStore(Store):

        u = reference(dm_cls=U, many=False)
        v = reference(dm_cls=V, many=False)

    U.new(t='foobar', doc_id='foo').save()
    V.new(t='foobar', doc_id='bar').save()

    s = UvStore.from_dict( {
        'u': (U, 'foo'),
        'v': (V, 'bar')
    }
    )

    print(s)

    struct = dict()
    struct['u'] = (U, 'foo')
    struct['v'] = (V, 'bar')
    store = UvStore.from_struct(struct=struct)

    assert store is not None

    # assert s is None

    u = s.u

    print(u)
    print(s.v)
