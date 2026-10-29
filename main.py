import os
import time
import requests
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 환경변수에서 GitHub Secrets 값 가져오기
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")

def generate_blog_content():
    """최신 Google GenAI SDK를 이용해 K-Vibe 영어 블로그 포스팅 내용 생성 (503 에러 자동 재시도 포함)"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        "Write an engaging blog post in English about Korean culture, lifestyle, "
        "or travel (K-Vibe). Provide the output strictly in the following format:\n"
        "TITLE: [Catchy Title Here]\n"
        "CONTENT: [HTML formatted body content suitable for a Blogger post]"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            text = response.text
            break
        except Exception as e:
            print(f"API 호출 중 오류 발생 ({attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("5초 후 재시도합니다...")
                time.sleep(5)
            else:
                raise e

    title = "K-Vibe Daily Post"
    content = text
    
    if "TITLE:" in text and "CONTENT:" in text:
        parts = text.split("CONTENT:")
        title_part = parts[0].replace("TITLE:", "").strip()
        if title_part:
            title = title_part
        content = parts[1].strip()
        
    return title, content

def post_to_blogger(title, content):
    """Blogger API를 이용해 구글 블로그에 글 발행"""
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    creds.refresh(Request())
    
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }
    body = {
        "title": title,
        "content": content
    }
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        print("블로그 포스팅 성공!")
    else:
        print(f"포스팅 실패: {response.text}")

if __name__ == "__main__":
    print("K-Vibe 자동 포스팅 스크립트 실행 중...")
    title, content = generate_blog_content()
    print(f"생성된 제목: {title}")
    post_to_blogger(title, content)
    print("완료!")
