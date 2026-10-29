import os
import requests
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# 환경변수에서 GitHub Secrets에 등록한 인증 정보 가져오기
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID") # 구글 블로그 ID

def generate_blog_content():
    """Gemini API를 이용해 K-Vibe 영어 블로그 포스팅 내용 생성"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = (
        "Write an engaging blog post in English about Korean culture, lifestyle, "
        "or travel (K-Vibe). Provide the output strictly in the following format:\n"
        "TITLE: [Catchy Title Here]\n"
        "CONTENT: [HTML formatted body content suitable for a Blogger post]"
    )
    
    response = model.generate_content(prompt)
    text = response.text
    
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
    
    # 토큰 갱신
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
