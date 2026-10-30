import os
import sys
import random
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests

# 1. 터미널 출력이 실시간으로 GitHub Actions 로그에 찍히도록 설정
sys.stdout.reconfigure(line_buffering=True)

print("=== [시작] K-Vibe 블로그 자동 발행 스크립트 실행 ===")

# 환경 변수 로드
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
BLOG_ID = os.environ.get("BLOG_ID")
PINTEREST_ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD_ID = os.environ.get("PINTEREST_BOARD_ID")

# --- 1. 무한 K-컬처 주제 생성 프롬프트 ---
K_CULTURE_PROMPTS = [
    "A hidden gem travel spot or scenic viewpoint in Korea (Seoul, Busan, Gyeongju, or Jeju) for international travelers.",
    "An iconic K-Drama or K-Movie filming location that fans can actually visit in South Korea.",
    "Authentic local Korean street food and night market guide for foodies.",
    "Unique Korean dessert cafes, vinyl bars, or aesthetic retro spots in Seoul.",
    "Korean daily lifestyle vibe: Han River picnic culture, 24-hour convenience store hacks, or self-photo booth trends.",
    "K-Pop star favorite hangouts, aesthetic cafes, or neighborhood tour guides in Korea."
]

selected_prompt_theme = random.choice(K_CULTURE_PROMPTS)
print(f"[1/4] 선택된 AI 글 주제 테마: {selected_prompt_theme}")

# --- 블로그 본문 및 썸네일에 들어갈 고화질 감성 이미지 풀 ---
SAMPLE_IMAGES = [
    "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?q=80&w=1000",
    "https://images.unsplash.com/photo-1517154421773-0529f29ea451?q=80&w=1000",
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=1000",
    "https://images.unsplash.com/photo-1546833999-b9f581a1996d?q=80&w=1000",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1000"
]
selected_image_url = random.choice(SAMPLE_IMAGES)

# --- 2. Gemini AI를 활용한 블로그 글 작성 ---
try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Write an engaging, highly-engaging English blog post about Korean culture based on this idea: {selected_prompt_theme}.
    
    Requirements:
    1. Title: Catchy, SEO-optimized title for Pinterest & Google search (Do NOT include 'Title:' prefix).
    2. Format: Clean HTML format with <h3> headings, paragraph tags <p>, and bold tags <b> for key points.
    3. Output Format:
    TITLE: [Your Blog Title Here]
    CONTENT:
    [Your HTML formatted blog post content here]
    """

    print("[2/4] Gemini AI 콘텐츠 생성 중...")
    response = ai_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    
    raw_text = response.text
    
    # 제목 및 본문 파싱
    if "TITLE:" in raw_text and "CONTENT:" in raw_text:
        title = raw_text.split("TITLE:")[1].split("CONTENT:")[0].strip()
        body_content = raw_text.split("CONTENT:")[1].strip()
    else:
        title = f"Discovering Korean Culture: {selected_prompt_theme}"
        body_content = f"<div>{raw_text}</div>"

    # 본문 맨 위에 대표 이미지 태그를 자동으로 넣어 썸네일 노출 보장
    content = f"""
    <div class="separator" style="clear: both; text-align: center; margin-bottom: 20px;">
        <img src="{selected_image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
    </div>
    {body_content}
    """

    print(f"-> 생성된 글 제목: {title}")

except Exception as e:
    print(f"❌ Gemini AI 글 생성 중 오류 발생: {e}")
    sys.exit(1)

# --- 3. Google Blogger API를 통한 포스팅 발행 ---
try:
    print("[3/4] 구글 블로거 API 연결 및 게시글 등록 중...")
    creds = Credentials(
