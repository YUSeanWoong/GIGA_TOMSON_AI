import os
import httpx
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env 파일에서 환경 변수를 불러옵니다.
# GitHub Actions에서는 .env 파일이 필요 없지만,
# 로컬 개발 환경을 위해 포함합니다.
load_dotenv()


# FastAPI 인스턴스를 생성합니다.
app = FastAPI(
    title="Gemini API 연동",
    description="Gemini API와 상호작용하는 간단한 FastAPI 애플리케이션입니다."
)

# 환경 변수에서 Gemini API 키를 설정합니다.
# GitHub Actions가 설정해준 환경 변수(GEMINI_API_KEY)를 읽어옵니다.
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    # API 키가 없으면 오류를 발생시킵니다.
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

# 사용할 Gemini 모델의 API 엔드포인트입니다.
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# 요청 본문을 위한 Pydantic 모델을 정의합니다.
class QuestionRequest(BaseModel):
    question: str

# 챗봇에 질문을 보내고 답변을 받는 API 엔드포인트입니다.
@app.post("/ask")
async def ask_chatbot(request: QuestionRequest):
    """
    Gemini 모델에 질문을 보내고 응답을 반환합니다.
    """
    try:
        # API 호출 전 로그로 토큰을 확인합니다.
        # 토큰의 일부만 출력하여 보안을 유지합니다.
        logger.info(f"Using API key starting with: {gemini_api_key[:5]}... and ending with: ...{gemini_api_key[-5:]}")
        
        # Gemini API 요청 페이로드를 생성합니다.
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": request.question
                        }
                    ]
                }
            ]
        }
        
        # httpx 클라이언트를 사용해 비동기적으로 API를 호출합니다.
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}?key={gemini_api_key}",
                json=payload
            )
            response.raise_for_status()  # HTTP 오류 발생 시 예외를 발생시킵니다.

        # 응답에서 답변 내용을 추출합니다.
        result = response.json()
        answer = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()

        if not answer:
            raise HTTPException(status_code=500, detail="API 응답 형식이 올바르지 않습니다.")
        
        # 질문과 생성된 답변을 반환합니다.
        return {"question": request.question, "answer": answer}

    except httpx.HTTPStatusError as e:
        # HTTP 오류 발생 시 상세 정보를 반환합니다.
        raise HTTPException(status_code=e.response.status_code, detail=f"Gemini API 오류: {e.response.text}")
    except Exception as e:
        # 기타 오류 발생 시 500 내부 서버 오류를 반환합니다.
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
