
def test_pypika():
    from pypika import Table, MySQLQuery as Query

    # history, customers = Table('history'), Table('customers')

    #     SELECT {order_s}.oid as oid, {product_s}.productName as productName
    #     FROM {order_s} LEFT JOIN {product_s} ON {order_s}.pid = {product_s}.productKey

    Order = Table('Order')
    Product = Table('Product')

    q = Query \
        .from_(Order) \
        .left_join(Product) \
        .on(Order.pid == Product.productKey) \
        .select(Order.oid.as_('oid'), Product.productName.as_('productName'))
    s = q.get_sql()
    assert s == ('SELECT `Order`.`oid` `oid`,`Product`.`productName` `productName` FROM '
                 '`Order` LEFT JOIN `Product` ON `Order`.`pid`=`Product`.`productKey`')


    # customers = Table('customers')
    # q = Query.from_(customers).select(
    #     customers.id, customers.fname, customers.lname, customers.phone)
    # s = q.get_sql()
    # assert s == ""
