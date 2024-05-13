import os


from django.conf import settings
from django.db import models
from django.db.models import Max, F

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50)
    sort_order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:  # 새 객체의 경우 id가 아직 없음
            max_sort_order = Category.objects.all().aggregate(Max('sort_order'))['sort_order__max']
            self.sort_order = (max_sort_order or 0) + 1
            print("추가된 category의 이름 : ", self.name ," sort_order  : ",self.sort_order)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Category.objects.filter(sort_order__gt=self.sort_order).update(sort_order=F('sort_order') - 1) 
    

class Section(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, null=False, related_name='sections', on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:  # 새 객체의 경우 id가 아직 없음
            max_sort_order = Section.objects.filter(category=self.category).aggregate(Max('sort_order'))['sort_order__max']
            self.sort_order = (max_sort_order or 0) + 1
            print("추가된 section의 sort_order : ", self.sort_order)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Section.objects.filter(category=self.category, sort_order__gt=self.sort_order).update(sort_order=F('sort_order') - 1) 
    
class Group(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, null=False, related_name='groups', on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:  # 새 객체의 경우 id가 아직 없음
            max_sort_order = Group.objects.filter(section=self.section).aggregate(Max('sort_order'))['sort_order__max']
            self.sort_order = (max_sort_order or 0) + 1
            print("추가된 group의 sort_order : ", self.sort_order)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Group.objects.filter(section=self.section, sort_order__gt=self.sort_order).update(sort_order=F('sort_order') - 1) 


class Folder(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, null=False, related_name='folders', on_delete=models.CASCADE)
    memo = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.id:  # 새 객체의 경우 id가 아직 없음
            max_sort_order = Folder.objects.filter(group=self.group).aggregate(Max('sort_order'))['sort_order__max']
            self.sort_order = (max_sort_order or 0) + 1
            print("추가된 folder의 sort_order : ", self.sort_order)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        Folder.objects.filter(group=self.group, sort_order__gt=self.sort_order).update(sort_order=F('sort_order') - 1) 



class Pdf(models.Model):
    name = models.CharField(max_length=255, blank=True)
    folder = models.ForeignKey(Folder, related_name='pdfs', on_delete=models.CASCADE)
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    sort_order = models.IntegerField(default=0)
    is_copied = models.BooleanField(default=False)  # 복사된 PDF 인지 여부를 나타내는 필드



    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.file:
            raise ValueError("File is required")
        if not self.name:
            self.name = os.path.splitext(os.path.basename(self.file.name))[0]
            # self.file.name의 경우 파일의 이름을 포함해 전체 파일 경로를 반환함
            # os.path.basename()는 파일 경로의 마지막 부분을 반환함
            # os.path.splitext()는 파일의 "이름.확장자" 에서  이름부분 / 확장자 부분을 나누어 튜플로 반환함
            # 이 튜플의 첫번째[0] 즉, 이름부분을 매칭시킨것임

        # PDF 객체가 새로 생성되는 경우 sort_order 설정
        if not self.id:  # 새 객체의 경우 id가 아직 없음
            max_sort_order = Pdf.objects.filter(folder=self.folder).aggregate(Max('sort_order'))['sort_order__max']
            # aggregate는 다양한 집계함수를 사용하기 위해 불러오며, 결과를 딕셔너리 형태로 반환한다. 이때 그 반환된 키:값은 "필드명__집계함수" : "값"의 형태이다
            # Max 집계함수로 'sort_order'필드의 최대값을 구함
            # 즉 최대값을 max_sort_order에 할당한 것임
            self.sort_order = (max_sort_order or 0) + 1
            print("추가된 pdf의 sort_order : ", self.sort_order)
            # 위까지 오버라이드, 그 이후에 아래에 원래의 기본 save 메서드로 저장
        super().save(*args, **kwargs)

    
    
    def delete(self, *args, **kwargs):
        if self.is_copied:  # 복사된 PDF 경우
            super().delete(*args, **kwargs)  # 물리적 파일은 삭제하지 않고 데이터베이스 레코드만 삭제
        else:
            # 원본 PDF의 경우, 동일한 파일을 참조하는 다른 복사본이 있는지 확인
            copies = Pdf.objects.filter(file=self.file, is_copied=True)
            if copies.exists():
                # 다른 복사본이 존재하면, 첫 번째 복사본을 원본으로 설정
                new_original = copies.first()
                new_original.is_copied = False
                new_original.save(update_fields=['is_copied'])
            else:
            # 파일이 실제로 존재하는지 확인
                if self.file:
                    # 파일 경로 가져오기
                    file_path = os.path.join(settings.MEDIA_ROOT, self.file.name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            super().delete(*args, **kwargs)

        # 지운 pdf보다 sort_order가 높은 애들 다 -1 씩 해줌
        Pdf.objects.filter(folder=self.folder, sort_order__gt=self.sort_order).update(sort_order=F('sort_order') - 1) 
        # __gt는 "greater than" (보다 큼)을 의미하는 Django의 필터링 표현
        # .update() 메소드는 필터링된 모든 객체를 한 번에 업데이트하는 방법
        # F 객체는 데이터베이스 필드 값에 대한 참조를 나타내며, 필드 값을 직접 변경하는 대신 데이터베이스 측에서 수학적 계산을 수행할 수 있게 합니다.
        

    