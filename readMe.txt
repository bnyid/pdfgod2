python version 3.11.9

[1] 첨에 clone 하면

OPENAI_API_KEY 와가 담긴 .env 
구글 text-to-speech 접근을 위한 bny-word-0e0713389fa7.json 

위 두개 파일을 루트 디렉토리에 넣어줘야함

[2] 구글 텍스트 투 스피치 접근권한 얻기
export GOOGLE_APPLICATION_CREDENTIALS="bny-word-0e0713389fa7.json"


[3] 음성작업을 위해 ffmpeg 설치 필요
brew install ffmpeg

* brew가 설치되어 있지 않으면
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"




[3] 






