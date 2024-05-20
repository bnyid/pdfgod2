import json
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ExcelUploadForm, TextInputForm
from google.cloud import texttospeech
from pydub import AudioSegment
import pandas as pd
import tempfile
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def wordgod_view(request):
    form = ExcelUploadForm()
    return render(request, 'wordgod.html', {'form': form})

def text_to_speech_with_google(text, language_code, voice_name, output_format="mp3"):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(response.audio_content)
    audio_segment = AudioSegment.from_file(temp_file_path, format=output_format)
    os.remove(temp_file_path)
    return audio_segment

def send_progress(progress):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "progress_group",
        {
            "type": "send_progress",
            "progress": progress,
        }
    )

def for_study(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Index', 'Word', 'Meaning']
            combined_audio = AudioSegment.empty()
            total_rows = len(df)
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
                progress = (index + 1) / total_rows * 100
                send_progress(progress)
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            combined_audio.export(output_path, format="mp3")
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="output_combined.mp3"'
                os.remove(output_path)
                return response
    else:
        form = ExcelUploadForm()
    return render(request, 'wordgod.html', {'form': form})

def for_exam(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file, header=None)
            df.columns = ['Index', 'Word', 'Meaning']
            combined_audio = AudioSegment.empty()
            total_rows = len(df)
            for index, row in df.iterrows():
                word = row['Word']
                for i in range(2):
                    audio_segment = text_to_speech_with_google(word, language_code='en-US', voice_name='en-US-Wavenet-D')
                    combined_audio += audio_segment
                    if i == 0:
                        combined_audio += AudioSegment.silent(duration=800)
                combined_audio += AudioSegment.silent(duration=7000)
                progress = (index + 1) / total_rows * 100
                send_progress(progress)
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