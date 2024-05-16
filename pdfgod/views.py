import json, io, os

from PyPDF2 import PdfMerger, PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont, pdfmetrics

from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import *
from .forms import *

font_path = os.path.join(settings.BASE_DIR, "static", "font", "NanumGothic.ttf")
pdfmetrics.registerFont(TTFont('NanumGothic', font_path))

# 메모 업데이트
@require_http_methods(["POST"])
def update_folder_memo(request, folder_id):
    print("update_folder_memo 함수가 호출되었씁니다.")
    try:
        data = json.loads(request.body)
        folder = Folder.objects.get(id=folder_id)
        folder.memo = mark_safe(data['memo'])
        folder.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(["POST"])
def paste_pdfs(request):
    try:
        data = json.loads(request.body)
        target_folder_id = data['target_folder_id']
        pdf_ids = data['pdf_ids']
        target_folder = Folder.objects.get(id=target_folder_id)
        new_pdfs = []

        for pdf_id in pdf_ids:
            pdf = Pdf.objects.get(id=pdf_id)
            new_pdf = Pdf(
                name=pdf.name,
                folder=target_folder,
                file=pdf.file,
                is_copied=True
            )
            new_pdf.save()
            new_pdfs.append(new_pdf)

        return JsonResponse({'success': True, 'message': f'{len(new_pdfs)} PDFs pasted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def mk_category(request):
    if request.method == 'POST':
        print("mk_category 함수가 호출되었습니다.")
        form = CategoryForm(data=request.POST)
        category_id = request.POST.get('category_id')
        print(form)
        if form.is_valid():
            new_category = form.save()
            print("new_category 가 데이터베이스에 저장되었습니다.")
            return redirect('index_with_category', category_id = new_category.id)
        else:
            return redirect('index')
        

def mk_section(request, category_id):
    print("mk_section 함수가 호출되었습니다.")
    if request.method == 'POST':
        print("post 요청입니다.")
        form = SectionForm(data=request.POST)
        if form.is_valid():
            new_section = form.save(commit=False)
            category = Category.objects.get(id=category_id)
            new_section.category = category
            new_section.save()
            print("new_section 이 데이터베이스에 저장되었습니다.")
            return redirect('index_with_category_section', category_id = category_id, section_id = new_section.id)
        else:
            return redirect('index')

def mk_group(request, category_id, section_id):
    print("mk_groupt 함수가 호출되었습니다.")
    if request.method == "POST":
        print("****************** mk_group의 if POST문 안으로 들어왔습니다.")        
        form = GroupForm(data=request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            section = Section.objects.get(id=section_id)
            new_group.section = section
            new_group.save()

            print("****************** new_group이 데이터베이스에 저장되었습니다.")        
            return redirect('index_with_category_section', category_id = category_id, section_id = section_id)
        else:
            return redirect('index')
        
def mk_folder(request, category_id, section_id, group_id):
    print("mk_folder 함수가 호출되었습니다.")
    if request.method == "POST":
        print("****************** mk_folder의 if == POST문 안으로 들어왔습니다.")        
        form = FolderForm(data=request.POST)
        if form.is_valid():
            new_folder = form.save(commit=False)
            group = Group.objects.get(id=group_id)
            new_folder.group = group
            new_folder.save()
            print("****************** new_folder가 데이터베이스에 저장되었습니다.")        
            return redirect('index_with_full_ids', category_id = category_id, section_id = section_id, group_id = group_id)
        else:
            return redirect('index')

def del_folder(request, category_id, section_id, group_id):
    print("del_folder 함수가 호출되었습니다.")
    if request.method == "POST":
        print("****************** del_folder의 if == POST문 안으로 들어왔습니다.")        
        folder_id=request.POST.get('folder_id')
        folder = Folder.objects.get(id=folder_id)
        folder.delete()
        return redirect('index_with_full_ids', category_id = category_id, section_id = section_id, group_id = group_id)
    

def upload_pdfs(request, category_id, section_id, group_id):
    print('upload_pdfs 함수가 호출되었습니다.')
    pdf_files = request.FILES.getlist('pdfs_upload')
    folder_id = request.POST.get('folder_id')
    if pdf_files:
        cur_folder = Folder.objects.get(id=folder_id)

        for pdf_file in pdf_files:
            pdf = Pdf(file=pdf_file, folder=cur_folder)
            pdf.save()
            print('pdf가 저장되었습니다.')
    return redirect('index_with_full_ids', category_id = category_id, section_id = section_id, group_id = group_id)


@require_http_methods(["POST"])
def copy_pdfs(request):  # 여기에 request 매개변수를 추가해야 합니다.
    try:
        print(request.POST)
        # 요청에서 PDF ID 목록과 목표 폴더 ID를 가져옵니다.
        pdf_ids = request.POST.getlist('pdf_ids')
        target_folder_id = request.POST.get('target_folder_id')
        
        # 목표 폴더 객체를 가져옵니다.
        target_folder = Folder.objects.get(id=target_folder_id)
        
        # 복사할 PDF 인스턴스를 생성합니다.
        new_pdfs = []
        for pdf_id in pdf_ids:
            original_pdf = Pdf.objects.get(id=pdf_id)
            new_pdf = Pdf(
                name=original_pdf.name,
                folder=target_folder,
                file=original_pdf.file,
                sort_order=original_pdf.sort_order,
                is_copied=True  # 복사된 PDF로 설정
            )
            new_pdf.save()
            new_pdfs.append(new_pdf)
        
        # 성공 응답을 보냅니다.
        return JsonResponse({'success': True, 'message': f'{len(new_pdfs)}개의 Pdf가 이동되었습니다.'})
    
    except Exception as e:
        # 에러 처리
        return JsonResponse({'success': False, 'error': str(e)})


        


def index(request, category_id=None, section_id=None, group_id=None):
    if category_id is None:
        category = Category.objects.first() 
        section = category.sections.first() if category else None
        group = section.groups.first() if section else None
    else:
        category = Category.objects.get(id=category_id)
        if section_id is None:
            section = category.sections.first() if category else None
            group = section.groups.first() if section else None
        else:
            section = Section.objects.get(id=section_id)
            if group_id is None:
                group = section.groups.first() if section else None
            else:
                group = Group.objects.get(id=group_id)
    
    # 각 구분클래스 인스턴스들
    categories = Category.objects.all()
    sections = category.sections.all() if category else Section.objects.none()
    groups = section.groups.all() if section else Group.objects.none()

    folders_with_pdfs = []
    if groups and group.folders:
        folders_with_pdfs = [(folder, list(folder.pdfs.all().order_by('sort_order'))) for folder in group.folders.all()]



    # 각 구분 클래스의 생성 Form
    form_category = CategoryForm()
    form_section = SectionForm()
    form_group = GroupForm()
    form_folder = FolderForm()



    context = {
        # 개별 클래스
        'category' : category,
        'section' : section,
        'group' : group,

        # 클래스 집합
        'categories' : categories,
        'sections' : sections,        
        'groups' : groups,        
        "folders_with_pdfs" : folders_with_pdfs,

        # 인스턴스 생성 폼
        'form_category' : form_category,
        'form_section' : form_section,
        'form_group' : form_group,
        'form_folder' : form_folder,
    }

    return render(request, 'index.html', context)



def move_pdf(request):
    data = json.loads(request.body)
    pdf_id = data.get('pdf_id')
    direction = data.get('direction')
    
    with transaction.atomic():  # 트랜잭션 시작
        try:
            target_pdf = Pdf.objects.select_for_update().get(id=pdf_id)
            if direction == 'up':
                previous_pdf = Pdf.objects.filter(folder=target_pdf.folder, sort_order__lt=target_pdf.sort_order).order_by('-sort_order').first()
                if previous_pdf:
                    previous_pdf.sort_order, target_pdf.sort_order = target_pdf.sort_order, previous_pdf.sort_order
                    previous_pdf.save()
                    target_pdf.save()
            elif direction == 'down':
                next_pdf = Pdf.objects.filter(folder=target_pdf.folder, sort_order__gt=target_pdf.sort_order).order_by('sort_order').first()
                if next_pdf:
                    next_pdf.sort_order, target_pdf.sort_order = target_pdf.sort_order, next_pdf.sort_order
                    next_pdf.save()
                    target_pdf.save()
            return JsonResponse({'success': True})
        except Pdf.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'PDF not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        


def del_pdfs(request):
    if request.method == 'POST':
        pdf_ids = request.POST.getlist('pdf_ids')
        
        for pdf_id in pdf_ids:
            pdf = Pdf.objects.get(id=pdf_id)
            pdf.delete()  # 개별 객체에 대해 delete 메소드 호출

    folder_id=request.POST.get('folder_id')    
    folder = Folder.objects.get(id=folder_id)
    group_id = folder.group.id
    section_id= folder.group.section.id
    category_id = folder.group.section.category.id
    return redirect('index_with_full_ids', category_id = category_id, section_id=section_id, group_id=group_id)


def merge_pdfs(request):
    if request.method == 'POST':
        cover_text = request.POST.get('cover_text', '')
        pdf_ids = request.POST.getlist('pdf_ids')
        merger = PdfMerger()

        # 선택된 PDF 파일 병합
        for pdf_id in pdf_ids:
            pdf = Pdf.objects.get(id=pdf_id)
            merger.append(open(pdf.file.path, 'rb'))

        # 병합된 PDF를 임시 파일로 저장
        temp_pdf_path = '/tmp/merged.pdf'
        with open(temp_pdf_path, 'wb') as f:
            merger.write(f)
        merger.close()

        # 텍스트가 입력된 경우 첫 페이지에 텍스트 추가
        if cover_text.strip():
            add_text_to_pdf(temp_pdf_path, cover_text)

        # 결과 PDF를 클라이언트에게 반환
        with open(temp_pdf_path, 'rb') as f:
            pdf_data = f.read()
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="merged.pdf"'
        return response

    return HttpResponse('Invalid request', status=400)


def add_text_to_pdf(pdf_path, text):
    # PDF를 읽습니다.
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    # 첫 페이지에 들어갈 텍스트를 생성합니다.
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont('NanumGothic', 10.5)  # 폰트 설정 (시스템에 설치된 폰트를 사용해야 함)

    # 텍스트 너비 계산
    text_width = c.stringWidth(text, 'NanumGothic', 12)
    
    # 페이지 너비와 높이
    page_width, page_height = letter
    
    # 텍스트 배치 좌표 계산
    x = ((page_width - text_width)) / 2
    y = page_height - 8  # 페이지 상단으로부터 50 포인트 아래

    c.drawString(x, y, text)
    c.save()

    # 생성된 텍스트 페이지를 읽습니다.
    packet.seek(0)
    new_pdf = PdfReader(packet)
    overlay_page = new_pdf.pages[0]

    # 첫 페이지와 텍스트 페이지 병합
    first_page = pdf_reader.pages[0]
    first_page.merge_page(overlay_page)
    pdf_writer.add_page(first_page)

    # 나머지 페이지 추가
    for page in pdf_reader.pages[1:]:
        pdf_writer.add_page(page)

    # 수정된 PDF 저장
    with open(pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)










@require_http_methods(["POST"])
def update_pdf_name(request, pdf_id):
    print("pdf이름 업로드 함수가 호출되었씁니다")
    try:
        data = json.loads(request.body)
        new_name = data['name']
        pdf = Pdf.objects.get(id=pdf_id)
        pdf.name = new_name
        pdf.save()
        return JsonResponse({'success': True})
    except Pdf.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'PDF not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})