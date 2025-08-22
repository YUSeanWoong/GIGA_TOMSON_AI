# 1. 베이스 이미지 (Python 3.11 사용)
FROM python:3.11-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 의존성 설치
# 로컬에 requirements.txt가 있다고 가정
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 앱 코드 복사
COPY . .

# 5. FastAPI가 0.0.0.0:8080에서 실행되도록 설정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]