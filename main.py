import os
import random
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 환경 변수에서 인증 정보 및 API 키 불러오기
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID", "koreadailylife24") # 블로그 ID 또는 주소

def generate_seo_blog_post():
    """Gemini API를 활용하여 SEO 최적화된 K-Vibe 영문 블로그 글 생성"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # K-Vibe 트렌디 주제 풀
    topics = [
        "Seoul's Hidden Rooftop Cafes with Stunning Sunset Views",
        "The Ultimate Guide to Traditional Korean Market Street Food in Gwangjang",
        "How to Spend a Perfect Rainy Day in Seoul Like a Local",
        "Must-Try Modern Korean Bakery Trends in Hongdae and Seongsu",
        "A Beginner's Guide to Korean Temple Stay and Healing Culture",
        "Top 5 Late-Night Delivery Foods You Must Order in Korea",
        "Exploring Seoul's Trendy Vinyl Listening Bars and Retro Cafes"
    ]
    selected_topic = random.choice(topics)
    
    prompt = f"""
    You are an expert SEO content creator specializing in Korean culture, lifestyle, travel, and trends (K-Vibe) for a global English-speaking audience.
    
    Please write a high-ranking, SEO-optimized blog post about this topic: "{selected_topic}".
    
    STRICT SEO REQUIREMENTS:
    1. Title: Catchy, engaging, includes high-volume search keywords related to the topic, under 60 characters.
    2. Structure: 
       - Introduction (include primary keywords naturally in the first 2 sentences)
       - 3-4 Subheadings (use <h2> and <h3> tags) with long-tail keywords
       - Bullet points (<ul>, <li>) for readability
       - A short FAQ section at the end (2-3 common questions with answers)
    3. Tone: Engaging, informative, natural English (avoid robotic AI phrasing).
    4. Formatting: Return valid HTML format for Blogger (use <h2>, <h3>, <p>, <ul>, <li>, <strong>). Do not wrap the output in markdown code blocks like ```html ... ```, just output the raw text structure requested below.

    You MUST strictly follow this output structure:
    TITLE: [Your SEO Title Here]
    CONTENT: [Your HTML Content Here]
    """
    
    print(f"Generating post for topic: {selected_topic}...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    
    text = response.text.strip()
    
    # TITLE과 CONTENT 파싱
    title = "K-Vibe Daily Life & Culture"
    content = text
    
    try:
        if "TITLE:" in text and "CONTENT:" in text:
            parts = text.split("CONTENT:")
            title_part = parts[0].replace("TITLE:", "").strip()
            content_part = parts[1].strip()
            if title_part:
                title = title_part
            if content_part:
                content = content_part
    except Exception as e:
        print(f"Parsing error (fallback to default title): {e}")
        
    return title, content

def post_to_blogger(title, content):
    """Blogger API를 통해 구글 블로그에 포스팅 업로드"""
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    service = build('blogger', 'v3', credentials=creds)
    
    body = {
        'title': title,
        'content': content,
        'labels': ['K-Vibe', 'Seoul Travel', 'Korean Culture', 'SEO Optimized']
    }
    
    # 블로그 ID 조회 또는 지정
    blogs = service.blogs().listByUser(userId='self').execute()
    blog_id = blogs['items'][0]['id']
    
    post = service.posts().insert(blogId=blog_id, body=body).execute()
    print(f"Successfully posted! Post URL: {post.get('url')}")

if __name__ == "__main__":
    post_title, post_content = generate_seo_blog_post()
    post_to_blogger(post_title, post_content)
