from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product, OrderItem, Order, Customer, Collection, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist  # wrap up the error
from django.db.models import Q, F, Func, Value, ExpressionWrapper, DecimalField
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem

# Create your views here.

# request -> response
# request handler
# action



def say_hello(request):
    #query_set = Product.objects.all()   # use this method to replace traditional SQL language
    # query_set is just like data table
    # try:
    #     product = Product.objects.get(pk = 1)
    # except ObjectDoesNotExist:
    #     pass
    # query_set = Product.objects.filter(unit_price__gt = 20)
    # exists = Product.objects.filter(pk=0).exists()  # will return the first element of the empty query set which will be null
    # # to get the specific record, pk is primary key
    query_set = Product.objects.filter(unit_price__range=(20, 30))  # product price between 20 30
    query_set = Product.objects.filter(collection__id__range = (1,2,3))  # product belongs to collection 1,2,3, external connection
    query_set = Product.objects.filter(title__contains='coffee') # case sensitive search which title contatins coffee
    query_set = Product.objects.filter(title__icontains='coffee') # case insensitive search
    query_set = Product.objects.filter(last_update__year=2021)
    query_set = Product.objects.filter(description__isnull = True )  # scription is null

    # multiple condition
    query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # query_set = Product.objects.filter(inventory__lt=10).filter(unit_price_lt=20)
    query_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt = 20))  # OR to combine two conditions
    query_set = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))  # ~ represents NOT

    # compare two keywords
    query_set = Product.objects.filter(inventory = F('unit_price'))
    query_set = Product.objects.filter(inventory=F('collection__id'))

    # sorting data
    query_set = Product.objects.order_by('title')
    query_set = Product.objects.order_by('-title')
    query_set = Product.objects.order_by('unit_price', '-title')
    query_set = Product.objects.order_by('unit_price', '-title').reverse()
    query_set = Product.objects.filter(collection__id=1).order_by('unit_price')
    #product = Product.objects.filter(collection__id=1).order_by('unit_price')[0] # return the first product
    product = Product.objects.earliest('unit_price')
    product = Product.objects.latest('unit_price')

    # limiting results
    query_set = Product.objects.all()[:5]

    # selecting fields
    query_set = Product.objects.values('id', 'title', 'collection__title')

    # select ordered products and sort them by title
    query_set = Product.objects.filter(id__in = OrderItem.objects.values('product__id').distinct()).order_by('title')

    # select related field
    query_set = Product.objects.select_related('collection').all() # combine two tables and we can select the columns from these two tables in html file
    # select_related only suitable for 1-to-1 relation
    # prefetch_related is suitable for many-to-many relation
    query_set = Product.objects.prefetch_related('promotions').all() # use Product table to connect with promotion table using key:promotions (many-to-many key)
    query_set = Product.objects.prefetch_related('promotions').select_related('collection').all()

    # get the last 5 orders with their customers and items including product
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    # django will create a reverse relationship between order and orderitem, but we need to set the related name in the orderitem
    # if we dont specify the related name, the field in the order model will be orderitem_set

    # aggregating
    # when collection id is 1, find the number of products and minimum price
    # result = Product.objects.filter(collection__id = 1).aggregate(count = Count('id'), min_price = Min('unit_price'))
    # return render(request, 'hello.html', {'name':'Yuan', 'result':result})

    # function method
    query_set = Customer.objects.annotate(
        # CONCATE
        full_name = Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    )

    # grouping data
    # get number of order of each customer
    # annotate is just creating a new field and the new field is calculated by different methods
    query_set = Customer.objects.annotate(
        order_count = Count("order")
    )

    # Expressionwrapper
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(
        discounted_price = discounted_price
    )

    # Generic Relationship using contenttype
    # we can use contenttype method to directly connect to the product model and we dont need to specify
    # the connection in the tag model.
    # 1. we need to specify which model to connect when we are calling the contenttype method and it will
    # return the content_type_id
    # 2. we use content_type_id in the taggeditem to find which model we want to use
    # 3. we use object_id to specify which product we want to see
    # both content_type and object are built-in fields
    content_type = ContentType.objects.get_for_model(Product)
    query_set = TaggedItem.objects.select_related('tag').filter(
        content_type = content_type,
        object_id = 1
    )

    # build custom manager
    query_set = TaggedItem.objects.get_tags_for(Product, 1)

    # creating objects/insert new record into table
    collection = Collection()
    collection.title = 'video games'
    collection.featured_product = Product(pk = 1)
    collection.save()

    # updating the table
    collection = Collection(pk = 11)
    collection.title = 'games'
    collection.featured_product = None
    collection.save()

    # when only update certain fields and keep other fields remain, we need to first output all the objects
    collection = Collection.objects.get(pk=12)
    collection.featured_product = None
    collection.save()
    # Collection.objects.filter(pk=12).update(featured_product=None) The second method

    # create a shopping cart with an item
    cart = Cart()
    cart.save()
    item1 = CartItem()
    item1.cart = cart  # connect to the cart
    item1.product = Product(pk=1)
    item1.quantity = 1
    item1.save()

    # change ultiple models and save multiple models and make the changes
    # however, when we change two models or more, if one model goes wrong, we need to roll back the entire operations
    # so we need to use transaction decoration function to decorate all the changes we want to include
    with transaction.atomic():
        order = Order()
        order.customer_id = 1
        order.save()

        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

    # raw SQL query
    query_set = Product.objects.raw('SELECT * FROM store_product')

    # second method
    # with connection.cursor() as cursor:
    #     cursor.execute("raw SQL query")

    return render(request, 'hello.html', {'name':'Yuan', 'result':list(query_set)})

