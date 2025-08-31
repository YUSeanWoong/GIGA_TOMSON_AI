# Python 3.11 버전의 공식 이미지를 사용합니다.
FROM python:3.11-slim

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 로컬의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY requirements.txt .

# requirements.txt에 명시된 모든 패키지를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 로컬의 모든 소스 코드 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . .

# 애플리케이션을 실행하는 명령어를 지정합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]