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

# --- 1. 참신하고 무한한 K-컬처 주제 생성 프롬프트 ---
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
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    raw_text = response.text
    
    # 제목 및 본문 파싱
    if "TITLE:" in raw_text and "CONTENT:" in raw_text:
        title = raw_text.split("TITLE:")[1].split("CONTENT:")[0].strip()
        content = raw_text.split("CONTENT:")[1].strip()
    else:
        title = f"Discovering Korean Culture: {selected_prompt_theme}"
        content = f"<div>{raw_text}</div>"

    print(f"-> 생성된 글 제목: {title}")

except Exception as e:
    print(f"❌ Gemini AI 글 생성 중 오류 발생: {e}")
    sys.exit(1)

# --- 3. Google Blogger API를 통한 포스팅 발행 ---
try:
    print("[3/4] 구글 블로거 API 연결 및 게시글 등록 중...")
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    blogger_service = build('blogger', 'v3', credentials=creds)
    
    body = {
        'kind': 'blogger#post',
        'title': title,
        'content': content,
        'labels': ['K-Vibe', 'Korea Travel', 'Korean Culture', 'SEO Optimized']
    }
    
    posts = blogger_service.posts()
    insert_request = posts.insert(blogId=BLOG_ID, body=body)
    new_post = insert_request.execute()
    
    post_url = new_post.get('url')
    print(f"✅ 구글 블로거 포스팅 완료! 게시글 URL: {post_url}")

except Exception as e:
    print(f"❌ 구글 블로거 포스팅 중 오류 발생: {e}")
    sys.exit(1)

# --- 4. Pinterest API 연동 (에러가 나도 스크립트가 튕기지 않도록 예외 처리) ---
print("[4/4] 핀터레스트 핀 발행 시도 중...")
if PINTEREST_ACCESS_TOKEN and PINTEREST_BOARD_ID:
    try:
        pinterest_url = "https://api.pinterest.com/v5/pins"
        headers = {
            "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
            "Content-Type": "json"
        }
        
        # 기본 스톡 대표 이미지 주소 (핀터레스트 필수값)
        default_image = "https://images.unsplash.com/photo-1517154421773-0529f29ea451?q=80&w=1000"
        
        payload = {
            "link": post_url,
            "title": title[:100],
            "description": f"Explore the latest K-Vibe trend: {title}",
            "board_id": PINTEREST_BOARD_ID,
            "media_source": {
                "source_type": "image_url",
                "url": default_image
            }
        }
        
        pin_res = requests.post(pinterest_url, json=payload, headers=headers)
        
        if pin_res.status_code == 201:
            print("✅ 핀터레스트 핀 발행 성공!")
        else:
            print(f"⚠️ [Pinterest Notice] 핀 발행 대기 중 ({pin_res.status_code}): {pin_res.text}")
            print("   (참고: 핀터레스트 Standard Access 승인 완료 전까지는 핀만 건너뛰고 블로그는 정상 발행됩니다.)")

    except Exception as e:
        print(f"⚠️ 핀터레스트 연동 중 예외 발생 (블로그 발행에는 영향 없음): {e}")
else:
    print("ℹ️ 핀터레스트 토큰 설정이 없어 핀터레스트 연동을 스킵합니다.")

print("=== [완료] 전체 자동화 프로세스가 성공적으로 끝났습니다 ===")
