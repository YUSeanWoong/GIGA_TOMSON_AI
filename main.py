import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Gemini API 연동",
    description="Gemini API와 상호작용하는 간단한 FastAPI 애플리케이션입니다."
)

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_chatbot(request: QuestionRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}?key={gemini_api_key}", # 키를 URL 파라미터로 전달dasdsa
                headers=HEADERS,
                json={"contents": [{"parts": [{"text": request.question}]}]}
            )
            response.raise_for_status()

        result = response.json()
        if not result or not result.get('candidates') or 'parts' not in result['candidates'][0]['content']:
            raise HTTPException(status_code=500, detail="API 응답 형식이 올바르지 않습니다.")
        
        answer = result['candidates'][0]['content']['parts'][0]['text']
        
        return {"question": request.question, "answer": answer}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API 오류: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {type(e).__name__} - {str(e)}")
