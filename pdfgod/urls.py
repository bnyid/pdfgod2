from django.urls import path, re_path
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
    path("del_folder/<int:folder_id>/", del_folder, name='del_folder'), 
    # re_path(r'^del_folder/(?P<category_id>\d*)/(?P<section_id>\d*)/(?P<group_id>\d*)/?$', del_folder, name='del_folder'), #인자를 선택적으로 받을수 있게 해줌 
    # r을 문자열 ''앞에 붙이면, 그 문자열에서는 \가 그냥 \로 해석됨. (즉 \n 이 줄바꿈을 의미하지 않게됨)
    # ^는 여기서부터 문자열이 시작된다는걸 의미?
    # (?P<category_id>\d+) 는 <int:category_id> 와 같은 역할 ?P<이름> 이 뒤에 올 d+(숫자)에 대해서 category_id라는 이름을 할당함. 이렇게 이름을 부여할땐 괄호()를 쳐줘야함
    # d는 \d+ 는 숫자 매칭 \d* 는 선택적 숫자 매칭

    

    # pdf
    path("upload_pdfs/<int:folder_id>/", upload_pdfs, name='upload_pdfs'),
    path("directUpload_pdfs/<int:category_id>/<int:section_id>/<int:group_id>", directUpload_pdfs, name='directUpload_pdfs'),
    path("del_pdfs/", del_pdfs, name= 'del_pdfs'),
    path("move_pdf/", move_pdf, name= 'move_pdf'),
    path("merge_pdfs/",merge_pdfs, name = 'merge_pdfs'),

    # api
    path('paste_pdfs/', paste_pdfs, name='paste_pdfs'),  # 붙여넣기
   
    #memo
    path('update-folder-memo/<int:folder_id>/', update_folder_memo, name='update-folder-memo'),
    path('update-pdf-name/<int:pdf_id>/', update_pdf_name, name='update_pdf_name'),

]