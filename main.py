import os
import requests

# ==========================================
# 1. 핀터레스트 자동 발행 함수
# ==========================================
def post_to_pinterest(title, description, link, image_url):
    """
    Pinterest API v5를 사용하여 핀(Pin)을 자동 생성합니다.
    """
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    board_id = os.environ.get("PINTEREST_BOARD_ID")

    if not access_token or not board_id:
        print("[Pinterest Warning] PINTEREST_ACCESS_TOKEN 또는 PINTEREST_BOARD_ID가 설정되지 않았습니다.")
        return

    url = "https://api.pinterest.com/v5/pins"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "board_id": board_id,
        "title": title[:100],        # 제목 최대 100자 제한
        "description": description[:800],  # 설명 최대 800자 제한
        "link": link,
        "media": {
            "media_source": {
                "source_type": "image_url",
                "url": image_url
            }
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"[Pinterest Success] 핀 업로드 성공! Pin ID: {response.json().get('id')}")
        else:
            print(f"[Pinterest Failed] 업로드 실패 ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[Pinterest Error] 예외 발생: {e}")


# ==========================================
# 2. 메인 실행 로직 (기존 블로그 자동화 로직)
# ==========================================
def run_automation():
    # --- [기존 블로그 생성 및 발행 로직 위치] ---
    # 예시: 기존 스크립트에서 발행된 블로그 글 정보를 변수에 담아옵니다.
    
    post_title = "K-Vibe Latest Trends and Style Guide"
    post_description = "Check out the new trend updates on K-Vibe Blogger!"
    post_url = "https://koreadailylife24.blogspot.com/"  # 실제 발행된 블로그 글 주소
    post_image = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f" # 블로그 썸네일 이미지 주소

    print("1. 구글 블로거 포스팅 완료.")

    # --- [3. 포스팅 완료 후 핀터레스트로 자동 전송] ---
    print("2. 핀터레스트 핀 발행 시작...")
    post_to_pinterest(
        title=post_title,
        description=post_description,
        link=post_url,
        image_url=post_image
    )

if __name__ == "__main__":
    run_automation()
