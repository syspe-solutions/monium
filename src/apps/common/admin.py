from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from apps.common.models import Address, DevelopmentRegion, Municipality, StoredFile


class BaseModelAdminAbstract(ImportExportModelAdmin):
    list_display = ('created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields if obj else self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # novo objeto
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Address)
class AddressAdmin(BaseModelAdminAbstract):
    list_display = ("street", "number", "city",
                    "district", "zip_code", "complement")
    search_fields = ("street", "city", "district", "zip_code")
    list_filter = ("city", "district")


class MunicipalityInline(admin.TabularInline):
    model = Municipality
    extra = 1 
    fields = ['name', 'ibge_code']


@admin.register(DevelopmentRegion)
class DevelopmentRegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym'] 
    search_fields = ['name', 'acronym']
    inlines = [MunicipalityInline]


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['name', 'ibge_code', 'region']
    list_filter = ['region']
    search_fields = ['name', 'ibge_code']
    
    
@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = ['relative_path', 'created_at', 'created_by']
    list_filter = ['created_at', 'created_by']
    search_fields = ['relative_path']  