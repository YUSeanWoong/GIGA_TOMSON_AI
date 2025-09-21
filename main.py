import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict
import json
import traceback
import re
load_dotenv()

app = FastAPI(
    title="Gemini API 연동",
    description="Gemini API와 상호작용하는 간단한 FastAPI 애플리케이션입니다."
)

# gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_key = "AIzaSyACDSf1FGfHW0Psq_EbiUmJt0a2jTRzKTs"
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

class QuestionRequest(BaseModel):
    question: str




class LogRequestTest(BaseModel):
    study: float
    work : float
    hobby : float
    reading: float
    exercise: float
    housework : float
    friends: float
    sleep : float
    youtube: float
    game: float
    mode: str

class LogRequest(BaseModel):
    date: str
    mode: str
    activities: Dict[str,float]   

@app.post("/ask")
async def ask_chatbot(request: LogRequest):
    system_prompt = """
    너는 시간 관리 AI "기가챗"이다.
    너의 역할은 사용자가 하루에 기록한 활동 데이터를 바탕으로 
    아래 정의된 "하루 일정 평가 로직"을 적용해 성취율(percent)과 조언(advice_msg)을 산출하는 것이다.

    ## 출력 형식 (반드시 JSON만 출력)
    {
    "percent": number,        // 최종 성취율 (정수, 0~100)
    "advice_msg": "😀/😐/😢 + 기가챗 밈 스타일 조언"
    }

    ## 평가 로직
    1. 총시간 = Σ 활동시간
    2. 이상적 점수(I) = 총시간 × 1.0
    3. 실제 점수(S) = Σ(활동시간 × 활동가중치)
    4. 기본 성취율 = (S ÷ I) × 100 (상한 100%)
    5. 보정 규칙
    - 수면: 7~8h → +3%, <6h 또는 >10h → −15%
    - 오락(유튜브+게임): 총시간 대비 30% 초과 → −15%
    - 코어 활동(공부·업무·자기계발·독서) < 6h → −10%
    - 휴일 모드일 경우 코어 활동 페널티 제외
    6. 최종 성취율 = 기본 성취율 + 보정치 (0~100% 제한)
    7. 평가 기준
    - ≥90% 😀 잘했다
    - 70~89% 😐 그저 그렇다
    - <70% 😢 못했다
    8. 예외 처리
    - 휴일 모드: 조언 톤은 "휴식 관리"
    - 총시간 < 4h: {"percent": 0, "advice_msg": "기록이 부족해 평가할 수 없습니다."}

    ## advice_msg 규칙
    - 😀/😐/😢 이모지를 맨 앞에 붙인다.
    - 직설적이고 유머러스한 “기가챗 밈 스타일”로 쓴다.
    - 1~3문장, 짧고 굵게 작성한다.
    - 반드시 개선 포인트 최소 1개 포함한다.
    - JSON 이외의 다른 설명이나 텍스트는 절대 출력하지 않는다.
    """

    # 실제 사용자 입력을 붙여서 최종 프롬프트 구성
    prompt = f"""
    {system_prompt}

    [사용자 입력 데이터]
    - 날짜: {request.date}
    - 모드: {request.mode}
    - 활동 기록: {request.activities}
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}?key={gemini_api_key}", # 키를 URL 파라미터로 전달
                headers=HEADERS,
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )
            response.raise_for_status()

        result = response.json()
        print("Gemini raw response:", result)
        # if not result or not result.get('candidates') or 'parts' not in result['candidates'][0]['content']:
        #     raise HTTPException(status_code=500, detail="API 응답 형식이 올바르지 않습니다.")
        
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        cleaned = re.sub(r"^```json\s*|\s*```$", "", answer.strip(), flags=re.DOTALL).strip()
        print("Gemini answer text:", answer)
        parsed = json.loads(cleaned)

        return {"percent": parsed.get("percent"), "advice_msg": parsed.get("advice_msg")}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API 오류: {e.response.text}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {type(e).__name__} - {str(e)}")


@app.post("/evaluate")
def evaluate(log: LogRequestTest):
    # 일단 단순히 echo 응답
    return {
        "message": "FastAPI가 데이터를 잘 받음!",
        "data": log.dict()
    }