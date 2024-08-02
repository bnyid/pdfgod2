from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from .forms import ExcelUploadForm
from google.cloud import texttospeech
from pydub import AudioSegment
import pandas as pd
import tempfile
import os, io
import urllib.parse
import zipfile

def wordgod_view(request):
    form = ExcelUploadForm()
    return render(request, 'wordgod.html', {'form': form})


from google.cloud import texttospeech
import io

def ssml_text_to_speech(ssml_text, language_code, voice_name):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(ssml=ssml_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    return AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")



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
        files = request.FILES.getlist('file')
        mp3_files = []
        for excel_file in files:
            combined_audio = AudioSegment.silent(duration=1500)  # 1.5초의 침묵

            logo_message_text = """
            <speak>
                <prosody rate="1.5" pitch="-2st">
                    <say-as interpret-as="characters">B&Y</say-as>
                </prosody>
            </speak>
            """
            logo_message = ssml_text_to_speech(logo_message_text, language_code='en-US', voice_name='en-US-Wavenet-D')
            combined_audio += logo_message

            intro_message = text_to_speech_with_google("Word Practice", language_code='en-US', voice_name='en-US-Wavenet-D')
            combined_audio += intro_message
            combined_audio += AudioSegment.silent(duration=2500)

            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Word', 'Meaning']

            for index, row in df.iterrows():
                word = row['Word']
                meaning = row['Meaning']
                for i in range(2):
                    audio_segment = text_to_speech_with_google(word, language_code='en-US', voice_name='en-US-Wavenet-D')
                    combined_audio += audio_segment
                    if i == 0:
                        combined_audio += AudioSegment.silent(duration=800)
                combined_audio += AudioSegment.silent(duration=800)
                audio_segment = text_to_speech_with_google(meaning, language_code='ko-KR', voice_name='ko-KR-Wavenet-A')
                combined_audio += audio_segment
                combined_audio += AudioSegment.silent(duration=800)

            base_filename = os.path.splitext(excel_file.name)[0]
            output_path = os.path.join(tempfile.gettempdir(), f"{base_filename}_학습용.mp3")
            combined_audio.export(output_path, format="mp3")
            mp3_files.append(output_path)

        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for mp3_file in mp3_files:
                zipf.write(mp3_file, os.path.basename(mp3_file))
                os.remove(mp3_file)

        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="output_학습용.zip"'
            os.remove(zip_path)
            return response
    return render(request, 'wordgod.html')


def for_exam(request):
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        mp3_files = []
        for excel_file in files:
            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Word', 'Meaning']
            total_words_count = len(df)
            combined_audio = AudioSegment.silent(duration=1500)

            logo_message_text = """
            <speak>
                <prosody rate="1.5" pitch="-2st">
                    <say-as interpret-as="characters">B&Y</say-as>
                </prosody>
            </speak>
            """
            logo_message = ssml_text_to_speech(logo_message_text, language_code='en-US', voice_name='en-US-Wavenet-D')
            combined_audio += logo_message

            intro_message = text_to_speech_with_google("Word test", language_code='en-US', voice_name='en-US-Wavenet-D')
            combined_audio += intro_message
            combined_audio += AudioSegment.silent(duration=2000)

            start_message = text_to_speech_with_google(f"총 {total_words_count}개의 단어 시험을 시작합니다", language_code='ko-KR', voice_name='ko-KR-Wavenet-A')
            combined_audio += start_message
            combined_audio += AudioSegment.silent(duration=1300)

            dingdong_path = os.path.join(settings.BASE_DIR, 'static', 'sound', 'dingdong.mp3')
            dingdong_sound = AudioSegment.from_file(dingdong_path, format="mp3")
            combined_audio += dingdong_sound
            combined_audio += AudioSegment.silent(duration=1500)

            for index, row in df.iterrows():
                word = row['Word']
                question_number = index + 1
                question_number_audio = text_to_speech_with_google(f"{question_number}번", language_code='ko-KR', voice_name='ko-KR-Wavenet-A')
                combined_audio += question_number_audio
                combined_audio += AudioSegment.silent(duration=1400)
                for i in range(2):
                    audio_segment = text_to_speech_with_google(word, language_code='en-US', voice_name='en-US-Wavenet-D')
                    combined_audio += audio_segment
                    combined_audio += AudioSegment.silent(duration=150)
                    if i == 0:
                        combined_audio += AudioSegment.silent(duration=800)
                
                combined_audio += AudioSegment.silent(duration=7500)
            combined_audio += dingdong_sound
            combined_audio += AudioSegment.silent(duration=1500)

            base_filename = os.path.splitext(excel_file.name)[0]
            output_path = os.path.join(tempfile.gettempdir(), f"{base_filename}_시험용.mp3")
            combined_audio.export(output_path, format="mp3")
            mp3_files.append(output_path)

        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for mp3_file in mp3_files:
                zipf.write(mp3_file, os.path.basename(mp3_file))
                os.remove(mp3_file)

        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="output_시험용.zip"'
            os.remove(zip_path)
            return response
    return render(request, 'wordgod.html')