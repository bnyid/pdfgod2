from django.shortcuts import render
from django.http import HttpResponse
from .forms import ExcelUploadForm, TextInputForm
from google.cloud import texttospeech
from pydub import AudioSegment
import pandas as pd
import tempfile
import os

def wordgod_view(request):
    form = ExcelUploadForm()
    return render(request, 'wordgod.html', {'form': form})

def text_to_speech_with_google(text, language_code, voice_name, output_format="mp3"):
    client = texttospeech.TextToSpeechClient()
    # Google Cloud Text-to-Speech 클라이언트를 초기화합니다.

    input_text = texttospeech.SynthesisInput(text=text)
    # 변환할 텍스트를 입력으로 설정합니다.

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )
    # 음성 합성을 위한 언어 코드와 음성 유형을 설정합니다.

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    # 오디오 출력 형식을 MP3로 설정합니다.

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    # 입력 텍스트와 설정된 음성 파라미터를 사용하여 음성을 합성합니다.

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(response.audio_content)
        # 합성된 음성 데이터를 임시 파일에 저장합니다.

    audio_segment = AudioSegment.from_file(temp_file_path, format=output_format)
    os.remove(temp_file_path)
    # 임시 파일에서 오디오 데이터를 읽어오고, 임시 파일을 삭제합니다.

    return audio_segment
    # 오디오 데이터를 반환합니다.

def for_study(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Index', 'Word', 'Meaning']
            # 업로드된 엑셀 파일을 읽어 데이터프레임으로 변환하고, 열 이름을 지정합니다.

            combined_audio = AudioSegment.empty()
            # 빈 오디오 시퀀스를 초기화합니다.

            for index, row in df.iterrows():
                word = row['Word']
                meaning = row['Meaning']
                # 각 행의 단어와 의미를 추출합니다.

                for i in range(2):
                    audio_segment = text_to_speech_with_google(word, language_code='en-US', voice_name='en-US-Wavenet-D')
                    combined_audio += audio_segment
                    if i == 0:
                        combined_audio += AudioSegment.silent(duration=800)

                combined_audio += AudioSegment.silent(duration=800)
                # 3초의 무음을 추가합니다.

                audio_segment = text_to_speech_with_google(meaning, language_code='ko-KR', voice_name='ko-KR-Wavenet-A')
                combined_audio += audio_segment
                # 의미를 한 번 읽고 오디오 시퀀스에 추가합니다.

                combined_audio += AudioSegment.silent(duration=800)
                # 2초의 무음을 추가합니다.

            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            combined_audio.export(output_path, format="mp3")
            # 최종 결합된 오디오 시퀀스를 MP3 파일로 저장합니다.

            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="output_combined.mp3"'
                os.remove(output_path)
                # 생성된 MP3 파일을 HTTP 응답으로 반환하고, 임시 파일을 삭제합니다.

                return response
    else:
        form = ExcelUploadForm()
        # GET 요청의 경우, 빈 폼을 렌더링합니다.

    return render(request, 'wordgod.html', {'form': form})
    # 템플릿에 폼을 전달하여 렌더링합니다.



def for_exam(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Index', 'Word', 'Meaning']
            
            combined_audio = AudioSegment.empty()
            
            for index, row in df.iterrows():
                word = row['Word']
                
                for i in range(2):
                    audio_segment = text_to_speech_with_google(word, language_code='en-US', voice_name='en-US-Wavenet-D')
                    combined_audio += audio_segment
                    if i == 0:
                        combined_audio += AudioSegment.silent(duration=800)

                combined_audio += AudioSegment.silent(duration=7000)
            
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            combined_audio.export(output_path, format="mp3")
            
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="exam_words.mp3"'
                os.remove(output_path)
                
                return response
    else:
        form = ExcelUploadForm()
    
    return render(request, 'wordgod.html', {'form': form})