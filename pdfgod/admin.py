from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Category)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['category','name']
    list_display_links = ['name']  # 'name' 필드를 클릭 가능하게 설정
    list_filter = ['category']
    search_fields = ['name']
    ordering = ['category', 'sort_order']

    class Media:
        css = {
            'all': ('css/admin.css',)  # 프로젝트에 맞는 경로로 수정하세요.
        }

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['get_category','section', 'name']
    list_display_links = ['name']  # 'name' 필드를 클릭 가능하게 설정
    list_filter = ['section__category', 'section']
    search_fields = ['name']
    ordering = ['section__category', 'section' ,'sort_order']

    def get_category(self, obj):
        return obj.section.category.name
    get_category.short_description = 'Category'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_category.admin_order_field = 'section__category__name'  # 정렬 가능하게 설정


    class Media:
        css = {
            'all': ('css/admin.css',)  # 프로젝트에 맞는 경로로 수정하세요.
        }

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['get_category','get_section','group', 'name']
    list_display_links = ['name']  # 'name' 필드를 클릭 가능하게 설정
    list_filter = ['group__section__category','group__section', 'group']
    search_fields = ['name']
    ordering = ['group__section__category','group__section', 'group' ,'sort_order']

    def get_section(self, obj):
        return obj.group.section.name
    get_section.short_description = 'Section'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_section.admin_order_field = 'group__section__name'  # 정렬 가능하게 설정

    def get_category(self, obj):
        return obj.group.section.category.name
    get_category.short_description = 'category'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_category.admin_order_field = 'group__section__category__name'  # 정렬 가능하게 설정

    class Media:
        css = {
            'all': ('css/admin.css',)  # 프로젝트에 맞는 경로로 수정하세요.
        }



@admin.register(Pdf)
class PdfAdmin(admin.ModelAdmin):
    list_display = ['get_category','get_section','get_group','folder', 'name']
    list_display_links = ['name']  # 'name' 필드를 클릭 가능하게 설정
    list_filter = ['folder__group__section__category','folder__group__section', 'folder__group', 'folder__group']
    search_fields = ['name']
    ordering = ['folder__group__section__category','folder__group__section', 'folder__group' ,'folder__group','sort_order']

    def get_category(self, obj):
        return obj.folder.group.section.category.name
    get_category.short_description = 'category'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_category.admin_order_field = 'folder__group__section__category__name'  # 정렬 가능하게 설정

    def get_section(self, obj):
        return obj.folder.group.section.name
    get_section.short_description = 'Section'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_section.admin_order_field = 'folder__group__section__name'  # 정렬 가능하게 설정

    def get_group(self, obj): 
        return obj.folder.group.name
    get_section.short_description = 'Group'  # Admin 인터페이스에서 보여질 컬럼 이름 설정
    get_section.admin_order_field = 'folder__group__name'  # 정렬 가능하게 설정

    class Media:
        css = {
            'all': ('css/admin.css',)  # 프로젝트에 맞는 경로로 수정하세요.
        }



