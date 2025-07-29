#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 완전 자동화된 블로그 포스팅 시스템 (Service Account 기반)
import os
import requests
import json
import time
import schedule
from datetime import datetime
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_keyword():
    """트렌드 키워드 자동 생성"""
    print('[LOG] Google Trends 키워드 자동 생성 시작')
    import random
    
    # 예비 키워드 (Google Trends API 문제로 인해 기본값 사용)
    fallback_keywords = [
        'AI', '인공지능', '클라우드', '빅데이터', '프로그래밍', '코딩',
        '증시', '주식', 'ETF', '투자', '재테크', '금융',
        '다이어트', '건강', '운동', '헬스', '영양', '생활',
        '여행', '골프', '등산', '취미', '문화', '라이프스타일',
        '기술', '소프트웨어', '개발', '웹', '모바일', '앱',
        '교육', '학습', '온라인', '디지털', '미래', '혁신'
    ]
    
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='ko', tz=540, timeout=(10,25), requests_args={'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}})
        
        # 한국 트렌딩 검색어 가져오기
        trending = pytrends.trending_searches(pn='south_korea')
        print(f'[DEBUG] pytrends 결과: {trending}')
        
        # 제외할 키워드
        exclude_keywords = [
            '정치', '대통령', '총선', '국회', '정당', '선거', '의원', '정부',
            '종교', '기독교', '불교', '천주교', '이슬람', '교회', '성당', '사찰',
            '전쟁', '전투', '군사', '군대', '폭격', '미사일', '핵', '침공', '분쟁'
        ]
        
        keywords = [str(k) for k in trending[0] if isinstance(k, str) and len(k) > 1 and not any(ex in str(k) for ex in exclude_keywords)]
        if keywords:
            selected_keyword = random.choice(keywords)
            print(f'[LOG] 선택된 키워드: {selected_keyword}')
            return selected_keyword
        else:
            raise Exception('pytrends에서 필터링 후 키워드를 찾을 수 없습니다.')
            
    except Exception as e:
        print(f'[ERROR] 키워드 생성 실패: {e}')
        selected_keyword = random.choice(fallback_keywords)
        print(f'[LOG] 예비 키워드 사용: {selected_keyword}')
        return selected_keyword

def generate_ai_content(topic):
    """AI로 블로그 포스트 생성"""
    print(f'[LOG] AI 글 생성 시작: {topic}')
    
    # API 키 검증
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_api_key:
        print('[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.')
        return None, None, None, None, None, None, "GEMINI_API_KEY 없음"
    
    prompt = f"""
다음 키워드에 대해 한글과 영어로 블로그 포스트를 작성해 주세요.
아래와 같이 반드시 JSON만 반환해 주세요. (body는 반드시 HTML로 작성)

{{
  "ko": {{
    "title": "키워드가 포함된 한글 제목",
    "body": "<h2>...</h2><p>...</p> ... (5000자 이상, SEO 최적화된 상세한 내용, HTML만 사용)",
    "tags": ["태그1", "태그2", "태그3", "태그4"]
  }},
  "en": {{
    "title": "English title with keyword",
    "body": "<h2>...</h2><p>...</p> ... (5000+ words, detailed SEO optimized content, HTML only)",
    "tags": ["tag1", "tag2", "tag3", "tag4"]
  }}
}}

요구사항:
- 한글 본문: 5000자 이상 (반드시 HTML로 작성)
- 영어 본문: 5000 words 이상 (반드시 HTML로 작성)
- SEO 최적화된 상세한 내용
- 독자에게 가치를 제공하는 실용적인 정보
- 키워드가 자연스럽게 포함된 제목과 내용
- body는 반드시 HTML로만 작성

키워드: {topic}
"""
    
    # 재시도 로직
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'[DEBUG] Gemini API 요청 시작 (시도 {attempt + 1}/{max_retries})')
            print(f'[DEBUG] API 키 확인: {gemini_api_key[:10]}...')
            
            response = requests.post(
                'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
                headers={'Content-Type': 'application/json'},
                params={'key': gemini_api_key},
                json={'contents': [{'parts': [{'text': prompt}]}]},
                timeout=60  # 타임아웃을 60초로 증가
            )
            
            print(f'[DEBUG] Gemini API 응답 상태: {response.status_code}')
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # 마크다운 제거
                content = re.sub(r'^[`\*\s]*json[\s`\*]*\n', '', content)
                content = re.sub(r'^```json\s*\n', '', content)
                content = re.sub(r'^```\s*\n', '', content)
                content = re.sub(r'\n```$', '', content)
                content = content.strip()
                
                try:
                    data = json.loads(content)
                    ko_title = data['ko']['title'].strip()
                    ko_body = data['ko']['body'].strip()
                    ko_tags = data['ko'].get('tags', [])
                    en_title = data['en']['title'].strip()
                    en_body = data['en']['body'].strip()
                    en_tags = data['en'].get('tags', [])
                    
                    print(f'[DEBUG] AI 글 생성 성공')
                    return ko_title, ko_body, en_title, en_body, ko_tags, en_tags, None
                except Exception as e:
                    print(f'[ERROR] JSON 파싱 실패: {e}')
                    if attempt == max_retries - 1:
                        return None, None, None, None, None, None, f"JSON 파싱 실패: {e}"
                    continue
            else:
                error_detail = response.text if response.text else "응답 내용 없음"
                print(f'[ERROR] Gemini API 호출 실패: {response.status_code} - {error_detail}')
                if attempt == max_retries - 1:
                    return None, None, None, None, None, None, f"API 호출 실패: {response.status_code} - {error_detail}"
                continue
                
        except requests.exceptions.Timeout as e:
            print(f'[ERROR] Gemini API 타임아웃 (시도 {attempt + 1}/{max_retries}): {e}')
            if attempt == max_retries - 1:
                return None, None, None, None, None, None, f"타임아웃 오류: {e}"
            time.sleep(5)  # 5초 대기 후 재시도
            continue
        except Exception as e:
            print(f'[ERROR] AI 글 생성 예외 (시도 {attempt + 1}/{max_retries}): {str(e)}')
            if attempt == max_retries - 1:
                return None, None, None, None, None, None, f"예외 발생: {str(e)}"
            time.sleep(5)  # 5초 대기 후 재시도
            continue
    
    return None, None, None, None, None, None, "최대 재시도 횟수 초과"

def get_service_account_service():
    """Service Account로 Blogger API 서비스 생성"""
    try:
        # 환경 변수에서 Service Account 키 가져오기
        sa_key_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if not sa_key_json:
            print('[ERROR] GOOGLE_APPLICATION_CREDENTIALS_JSON 환경 변수가 설정되지 않았습니다.')
            return None
        
        # 임시 파일로 Service Account 키 저장
        import tempfile
        import json
        
        # JSON 파싱하여 유효성 검사
        try:
            sa_key_data = json.loads(sa_key_json)
        except json.JSONDecodeError as e:
            print(f'[ERROR] Service Account 키 JSON 파싱 실패: {e}')
            return None
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(sa_key_data, tmp_file)
            key_file = tmp_file.name
        
        print(f'[DEBUG] Service Account 키 파일 생성: {key_file}')
        
        # Service Account 인증 정보 생성
        credentials = service_account.Credentials.from_service_account_file(
            key_file,
            scopes=['https://www.googleapis.com/auth/blogger']
        )
        
        # 임시 파일 삭제
        os.unlink(key_file)
        
        # Blogger API 서비스 생성
        service = build('blogger', 'v3', credentials=credentials)
        print('[LOG] Service Account 인증 성공')
        return service
        
    except Exception as e:
        print(f'[ERROR] Service Account 인증 실패: {e}')
        return None

def post_to_blogger_auto(title, content, labels=None):
    """Service Account로 자동 포스팅"""
    print(f'[LOG] 자동 블로거 포스팅 시작: {title}')
    
    service = get_service_account_service()
    if not service:
        return {'title': title, 'url': 'ERROR: Service Account 인증 실패'}
    
    BLOG_ID = os.environ.get('BLOG_ID')
    if not BLOG_ID:
        return {'title': title, 'url': 'ERROR: BLOG_ID 없음'}
    
    try:
        # 포스트 생성
        post = service.posts().insert(
            blogId=BLOG_ID,
            body={
                'title': title,
                'content': content,
                'labels': labels or []
            }
        ).execute()
        
        print(f'[LOG] 자동 포스팅 성공: {post.get("url", "")}')
        return {'title': post.get('title', title), 'url': post.get('url', '')}
        
    except Exception as e:
        print(f'[ERROR] 자동 포스팅 실패: {e}')
        return {'title': title, 'url': f"ERROR: {e}"}

def generate_images_auto(topic, count=1):
    """AI 이미지 자동 생성"""
    print(f'[LOG] AI 이미지 자동 생성 시작: {topic}')
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            headers={"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY')}"},
            json={"inputs": f"high quality, professional, {topic}"}
        )
        
        if response.status_code == 200:
            # 이미지를 임시 파일로 저장
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(response.content)
                image_path = tmp_file.name
            
            print(f'[LOG] 이미지 생성 성공: {image_path}')
            return [image_path]
        else:
            print(f'[ERROR] 이미지 생성 실패: {response.status_code}')
            return []
    except Exception as e:
        print(f'[ERROR] 이미지 생성 예외: {e}')
        return []

def add_images_to_html_auto(html_content, images):
    """HTML에 이미지 자동 추가"""
    if not images:
        return html_content
    
    image_html = ""
    for i, image_path in enumerate(images):
        # 이미지를 base64로 인코딩하여 HTML에 직접 삽입
        import base64
        with open(image_path, 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        
        image_html += f'<div style="text-align: center; margin: 20px 0;">'
        image_html += f'<img src="data:image/jpeg;base64,{img_data}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" alt="AI 생성 이미지 {i+1}">'
        image_html += f'</div>'
        
        # 임시 파일 삭제
        os.unlink(image_path)
    
    if image_html:
        if '<h2>' in html_content:
            parts = html_content.split('<h2>', 1)
            if len(parts) > 1:
                html_content = parts[0] + '<h2>' + parts[1].split('</h2>', 1)[0] + '</h2>' + image_html + '<p>' + parts[1].split('</h2>', 1)[1] + '</p>'
        else:
            html_content = image_html + html_content
    
    return html_content

def create_blog_html_auto(content, images=None):
    """블로그 포스트용 HTML 자동 생성"""
    html_content = content
    if images:
        html_content = add_images_to_html_auto(html_content, images)
    
    full_html = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333;">
        {html_content}
    </div>
    """
    return full_html

def auto_workflow():
    """완전 자동화된 워크플로우"""
    print('[LOG] 완전 자동화 워크플로우 시작')
    
    try:
        # 1. 키워드 자동 생성
        topic = get_keyword()
        
        # 2. AI 글 자동 생성
        ko_title, ko_body, en_title, en_body, ko_tags, en_tags, error = generate_ai_content(topic)
        if error:
            print(f'[ERROR] AI 글 생성 실패: {error}')
            return f"AI 글 생성 실패: {error}"
        
        # 3. 이미지 자동 생성
        images = generate_images_auto(topic, 1)
        
        # 4. 한글 포스트 자동 생성 및 포스팅
        ko_html = create_blog_html_auto(ko_body, images)
        ko_result = post_to_blogger_auto(ko_title, ko_html, ko_tags)
        
        # 5. 영어 포스트 자동 생성 및 포스팅
        en_html = create_blog_html_auto(en_body, images)
        en_result = post_to_blogger_auto(en_title, en_html, en_tags)
        
        # 6. 결과 로그
        print(f'[SUCCESS] 자동 포스팅 완료!')
        print(f'[INFO] 한글 포스트: {ko_result.get("url", "실패")}')
        print(f'[INFO] 영어 포스트: {en_result.get("url", "실패")}')
        
        return {
            'ko_post': ko_result,
            'en_post': en_result,
            'topic': topic
        }
        
    except Exception as e:
        print(f'[ERROR] 자동 워크플로우 실패: {e}')
        return f"자동 워크플로우 실패: {e}"

def handler(request):
    """Cloud Functions 핸들러"""
    print('[LOG] Cloud Function 호출됨')
    
    try:
        result = auto_workflow()
        
        if isinstance(result, dict):
            return {
                'status': 'success',
                'message': '자동 포스팅 완료',
                'data': result
            }
        else:
            return {
                'status': 'error',
                'message': result
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'예외 발생: {str(e)}'
        }

def start_auto_scheduler():
    """자동 스케줄러 시작"""
    print('[LOG] 자동 스케줄러 시작')
    
    # 매 6시간마다 자동 포스팅
    schedule.every(6).hours.do(auto_workflow)
    
    # 시작 시 즉시 한 번 실행
    auto_workflow()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == '__main__':
    print('완전 자동화된 블로그 포스팅 시스템')
    print('='*50)
    
    # 단일 실행
    result = auto_workflow()
    print(f'결과: {result}') 