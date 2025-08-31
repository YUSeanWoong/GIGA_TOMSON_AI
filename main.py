from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 불러옵니다.
load_dotenv()

# FastAPI 인스턴스를 생성합니다.
app = FastAPI(
    title="GPT API 연동",
    description="OpenAI API와 상호작용하는 간단한 FastAPI 애플리케이션입니다."
)

# 환경 변수에서 OpenAI API 키를 설정합니다.
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    # API 키가 없으면 오류를 발생시킵니다.
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# OpenAI 클라이언트를 초기화합니다.
client = OpenAI(api_key=openai_api_key)

# 요청 본문을 위한 Pydantic 모델을 정의합니다.
class QuestionRequest(BaseModel):
    question: str

# GPT에 질문을 보내고 답변을 받는 API 엔드포인트입니다.
@app.post("/ask")
async def ask_gpt(request: QuestionRequest):
    """
    GPT 모델에 질문을 보내고 응답을 반환합니다.
    """
    try:
        # OpenAI API를 호출하여 응답을 받습니다.
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # 다른 모델로 변경할 수 있습니다 (예: "gpt-3.5-turbo").
            messages=[
                {"role": "user", "content": request.question}
            ]
        )

        # 응답에서 답변 내용을 추출합니다.
        answer = completion.choices[0].message.content
        
        # 질문과 생성된 답변을 반환합니다.
        return {"question": request.question, "answer": answer}

    except Exception as e:
        # 오류 발생 시 500 내부 서버 오류를 반환합니다.
        raise HTTPException(status_code=500, detail=str(e))
