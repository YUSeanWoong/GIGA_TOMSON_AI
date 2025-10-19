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

gemini_api_key = os.getenv("GEMINI_API_KEY")



if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
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
    "advice_msg": "// + 기가챗 밈 스타일 조언"
    }

    평가 로직
    활동 가중치
    코어 활동(공부·업무·자기계발·독서): 1.2

    수면: 0.8

    오락(유튜브+게임): 0.3

    운동: 1.0

    집안일 : 0.85

    친목 : 0.85

    수면 : 별도 보정 규칙



    점수 계산
    총시간 = Σ 활동시간

    이상적 점수(I) = 총시간 × 1.2

    실제 점수(S) = Σ(활동시간 × 활동가중치)

    기본 성취율 = (S ÷ I) × 100



    보정 규칙
    수면: 7~8h → +3%, <6h 또는 >10h → −15%

    코어 활동(공부·업무·자기계발·독서): < 6h → −10%

    오락(유튜브+게임): 2h 초과 시, 초과한 1h당 −5% 추가 차감



    최종 성취율 = 기본 성취율 + 보정치 (0~100% 제한)



    평가 기준
    ≥90% 잘했다

    70~89% 그저 그렇다

    <70% 못했다



    예외 처리
    휴일 모드: 조언 톤은 "휴식 관리"

    총시간 < 4h: {"percent": 0, "advice_msg": "기록이 부족해 평가할 수 없습니다."}



    advice_msg 규칙
    //웃음, 무표정, 슬픔 이모지를 맨 앞에 붙인다.

    직설적이고 유머러스하며 해학적인 거친 남성의 말투로 표현한다.

    특정 직업이나 상황의 비속어는 사용하지 않는다.

    1~3문장, 짧고 굵게 작성한다.

    계산식에 대한 정보는 출력하지 않는다.

    반드시 개선 포인트 최소 1개 포함한다.

    잘했을 땐 확실하게 칭찬하고, 못했을 땐 확실하게 다그친다.

    활동 시간을 임의로 합산하거나 재해석하지 않고, 주어진 활동 시간 그대로를 기반으로 조언한다.

    JSON 이외의 다른 설명이나 텍스트는 절대 출력하지 않는다.
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