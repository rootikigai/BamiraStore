from django.contrib import admin

from store.models import Product, Collection, ProductImage


# Register your models here.
# admin.site.register(Product)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [ 'title', 'description', 'price', 'inventory', 'updated_at', 'collection']
    list_per_page = 10
    search_fields = ['title', 'description']
    list_editable = ['price', 'inventory']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'product', 'image' ]
