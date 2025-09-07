import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 불러옵니다.
load_dotenv()


# FastAPI 인스턴스를 생성합니다.
app = FastAPI(
    title="Hugging Face API 연동",
    description="Hugging Face API와 상호작용하는 간단한 FastAPI 애플리케이션입니다."
)

# 환경 변수에서 Hugging Face API 키를 설정합니다.
hugging_face_api_key = ${{ secrets.HUGGING_FACE_API_KEY }}
if not hugging_face_api_key:
    # API 키가 없으면 오류를 발생시킵니다.
    raise ValueError("HUGGING_FACE_API_KEY 환경 변수가 설정되지 않았습니다.")

# 사용할 Hugging Face 모델의 API 엔드포인트입니다.
# 다른 모델을 사용하려면 이곳을 변경하세요.
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {hugging_face_api_key}"}

# 요청 본문을 위한 Pydantic 모델을 정의합니다.
class QuestionRequest(BaseModel):
    question: str

# 챗봇에 질문을 보내고 답변을 받는 API 엔드포인트입니다.
@app.post("/ask")
async def ask_chatbot(request: QuestionRequest):
    """
    Hugging Face 모델에 질문을 보내고 응답을 반환합니다.
    """
    try:
        # httpx 클라이언트를 사용해 비동기적으로 API를 호출합니다.
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL,
                headers=HEADERS,
                json={"inputs": f"[INST] {request.question} [/INST]"}
            )
            response.raise_for_status()  # HTTP 오류 발생 시 예외를 발생시킵니다.

        # 응답에서 답변 내용을 추출합니다.
        result = response.json()
        if not result or 'generated_text' not in result[0]:
            raise HTTPException(status_code=500, detail="API 응답 형식이 올바르지 않습니다.")
        
        # Mistral 모델의 응답 형식에서 답변만 추출합니다.
        answer = result[0]['generated_text'].split('[/INST]')[-1].strip()
        
        # 질문과 생성된 답변을 반환합니다.
        return {"question": request.question, "answer": answer}

    except httpx.HTTPStatusError as e:
        # HTTP 오류 발생 시 상세 정보를 반환합니다.
        raise HTTPException(status_code=e.response.status_code, detail=f"Hugging Face API 오류: {e.response.text}")
    except Exception as e:
        # 기타 오류 발생 시 500 내부 서버 오류를 반환합니다.
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
