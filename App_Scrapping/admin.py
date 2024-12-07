from django.contrib import admin

# Register your models here.
from .models import ScrapedData

class ScrapedDatatable(admin.ModelAdmin):
    list_display = ['id','title','url','scraped_at']
    search_fields = ( 'url',)

admin.site.register(ScrapedData,ScrapedDatatable)