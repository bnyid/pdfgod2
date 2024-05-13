from django.urls import path
from .views import *

urlpatterns = [ 

    # index
    path("", index,name='index'),
    path("<int:category_id>/", index, name='index_with_category'),
    path("<int:category_id>/<int:section_id>/", index, name='index_with_category_section'),
    path("<int:category_id>/<int:section_id>/<int:group_id>/", index, name='index_with_full_ids'),

    # category
    path("mk_category/", mk_category, name='mk_category'),

    # section
    path("mk_section/<int:category_id>/", mk_section, name='mk_section'),

    # group
    path("mk_group/<int:category_id>/<int:section_id>", mk_group, name='mk_group'),

    # folder
    path("mk_folder/<int:category_id>/<int:section_id>/<int:group_id>", mk_folder, name='mk_folder'),
    path("del_folder/<int:category_id>/<int:section_id>/<int:group_id>", del_folder, name='del_folder'),

    # pdf
    path("upload_pdfs/<int:category_id>/<int:section_id>/<int:group_id>", upload_pdfs, name='upload_pdfs'),
    path("del_pdfs/", del_pdfs, name= 'del_pdfs'),
    path("move_pdf/", move_pdf, name= 'move_pdf'),
    path("merge_pdfs/",merge_pdfs, name = 'merge_pdfs'),

    # api
    path('paste_pdfs/', paste_pdfs, name='paste_pdfs'),  # 붙여넣기
   
    #memo
    path('update-folder-memo/<int:folder_id>/', update_folder_memo, name='update-folder-memo'),
]