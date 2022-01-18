from django.contrib import admin, messages  # messages is defined to return error messages
from . import models
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.utils.html import format_html, urlencode
from django.urls import reverse
# Register your models here.

class InventoryFilter(admin.SimpleListFilter): # we create another filter by using the custom columns like inventory_status
    title = 'inventory'  # filter's name
    parameter_name = 'inventory'  # the field in the product model that we want to filter, like collection (in product model) collection__id is what we want to filter.

    def lookups(self, request, model_admin):  # the selection we can select from the filter
        return [
            ('<10', 'Low') # each tuple represents one selection, for each tuple, the first element is condition for the real values and the second value represents the
        ]

    def queryset(self, request, queryset):  # build the filter using query
        if self.value() == '<10':  # if we select this selection, start a query set
            return queryset.filter(inventory__lt = 10)

class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']  # autocomplete and autosearch the value whenever we input a value, but we need to add a search field in the collectionadmin
    prepopulated_fields = {
        'slug':['title']
    }  # prepopulated_fields are designed to automatically generate some fields like slug when we input our product title
    actions = ['clear_inventory']  # need to define this method first and we will build function to specify this method
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title', 'collection_feature_product']  # we need specific fields in the related models
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']  # used for related fields
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']
    # search_fields = ['']

    def collection_title(self, product):
        return product.collection.title

    def collection_feature_product(self, product):
        return product.collection.featured_product

    @admin.display(ordering='inventory')  # make the column orderable
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'low'
        return 'ok'
    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were updated successfully",
            messages.ERROR
        )


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']  # add a search area in the customer page to search by name and the input should match the initial value of first and last name
    # istartswith means insensitive to the upper and lower case letter

class OrderItemInline(admin.TabularInline):  # Then we can edit children model in the parent model
    model = models.OrderItem
    extra = 1
    autocomplete_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer_first_name', 'customer_last_name']
    list_select_related = ['customer']

    def customer_first_name(self, Order):
        return Order.customer.first_name
    def customer_last_name(self, Order):
        return Order.customer.last_name

# adeverse field for the models, for example, we need to see the number of product in each collection
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    search_fields = ['title']
    # for the non-exsit column in collection, we need to use function to define
    @admin.display(ordering='product_count')
    def product_count(self, collection):
        url = reverse('admin:store_product_changelist')  # When we need to link to custom webpage, we need to use reverse function to change the format: admin:app_model_page to
        # normal url and let href = url. page includes changelist, add, history, delete, etc,but when we click into the link of each collection type, it will return all the product with all types
        # url = reverse(
        #     reverse('admin:store_product_changelist')
        #     + '?'  # means start query
        #     + urlencode({  # means change they query to url
        #         'collection__id': str(collection.id)
        #     })
        # )
        return format_html('<a href="{}">{}</a>',url, collection.product_count) # we can change the product count to a link which will link to google.com

    # We can also use SQL method to calculate the new columns
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('product')
        )

admin.site.register(models.Collection, CollectionAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Order, OrderAdmin)
