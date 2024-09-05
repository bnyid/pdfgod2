import openai
from django.shortcuts import render
from django.conf import settings
from openai import OpenA

openai_api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=openai_api_key)

model_id = 'ft:gpt-4o-2024-08-06:personal::A41eiFDG'

system_prompt = """
You are an assistant trained to generate multiple-choice questions based on a given passage. Your task is to analyze the passage and create two multiple-choice questions: one that asks for the main idea or topic, and another that asks for an appropriate title. Each question should have several answer choices. You will also provide the correct answers.

Follow this structure:

1. Read the passage carefully.
2. Create a question asking for the main idea or topic of the passage. Provide 10 answer choices.
3. Create a question asking for an appropriate title of the passage. Provide 10 answer choices.
4. Clearly indicate the correct answers for both questions.
5. Ensure that the number of correct answers for each question does not exceed 4.

Here is an example of what your output should look like:

[Passage]
{Insert passage here}

A. 적절한 주제와 요지를 고르세요
① [First answer choice]
② [Second answer choice]
...
⑩ [Tenth answer choice]

B. 적절한 제목을 고르세요
① [First answer choice]
② [Second answer choice]
...
⑩ [Tenth answer choice]

[Answer]
A. [Correct answer(s) for the main idea or topic]
B. [Correct answer(s) for the title] 

Now, generate the questions and answers based on the passage provided below.
"""

def index(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        if user_input:
            # OpenAI의 최신 API 호출 방식
            response = client.chat.completions.create(
                model = model_id,  # 또는 사용 중인 다른 모델
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            output_text = response.choices[0].message.content
            return render(request, 'fine.html', {'output_text': output_text})
    
    return render(request, 'fine.html')


