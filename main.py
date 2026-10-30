import os
import random
import requests
from google import genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 환경 변수 및 API 키 설정
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID", "koreadailylife24")

# 전달해주신 Unsplash API Access Key 적용
UNSPLASH_ACCESS_KEY = "qPh-5iEtu1QI7-w2FuXNCqz2GCwKS-7oAuYT5xSfWFU"

def get_unsplash_image_url(query):
    """Unsplash 공식 API를 호출하여 키워드에 맞는 가장 어울리는 고화질 이미지 URL 가져오기"""
    try:
        url = f"https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                # 고화질 이미지 URL 추출 (regular 사이즈)
                image_url = data["results"][0]["urls"]["regular"]
                print(f"Successfully fetched Unsplash image for query '{query}'")
                return image_url
    except Exception as e:
        print(f"Unsplash API error: {e}")
        
    # API 호출 실패 시 대체 기본 이미지
    return "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80"

def get_trending_kvibe_topic():
    """K-Vibe 트렌디 키워드 풀에서 무작위 선택"""
    trending_topics = [
        "Seoul's Hidden Rooftop Cafes with Stunning Sunset Views",
        "The Ultimate Guide to Traditional Korean Market Street Food in Gwangjang",
        "How to Spend a Perfect Rainy Day in Seoul Like a Local",
        "Must-Try Modern Korean Bakery Trends in Hongdae and Seongsu",
        "A Beginner's Guide to Korean Temple Stay and Healing Culture",
        "Top 5 Late-Night Delivery Foods You Must Order in Korea",
        "Exploring Seoul's Trendy Vinyl Listening Bars and Retro Cafes",
        "Best Spots to Experience Autumn Foliage in Seoul Palaces",
        "Trending K-Fashion Styling Tips from Seongsu-dong Streets",
        "A Complete Guide to Korean Convenience Store Must-Eat Snacks"
    ]
    return random.choice(trending_topics)

def generate_seo_blog_post():
    """Gemini API로 SEO 최적화 글 작성 및 Unsplash 이미지 결합"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    selected_topic = get_trending_kvibe_topic()
    
    # 주제에서 Unsplash 검색에 쓸 핵심 키워드 추출 (예: 'Seoul Rooftop Cafe')
    search_keyword = selected_topic.replace("Best Spots to Experience", "").replace("The Ultimate Guide to", "").strip()
    image_url = get_unsplash_image_url(search_keyword)
    
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
        model="gemini-3.8-flash",
        contents=prompt,
    )
    
    text = response.text.strip()
    
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
        
    # Unsplash 고화질 이미지를 본문 맨 위에 HTML로 삽입
    image_html = f'''
    <div class="separator" style="clear: both; text-align: center; margin-bottom: 25px;">
        <a href="{image_url}" style="margin-left: 1em; margin-right: 1em;">
            <img border="0" data-original-height="800" data-original-width="1200" src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
        </a>
    </div>
    '''
    
    final_content = image_html + content
    return title, final_content

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
        'labels': ['K-Vibe', 'Seoul Travel', 'Korean Culture', 'SEO Optimized', 'Unsplash']
    }
    
    blogs = service.blogs().listByUser(userId='self').execute()
    blog_id = blogs['items'][0]['id']
    
    post = service.posts().insert(blogId=blog_id, body=body).execute()
    print(f"Successfully posted! Post URL: {post.get('url')}")

if __name__ == "__main__":
    post_title, post_content = generate_seo_blog_post()
    post_to_blogger(post_title, post_content)
