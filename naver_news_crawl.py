import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parse_search_results(search_html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(search_html, "html.parser")
    news_links: list[dict[str, str]] = []

    # 네이버 검색 결과에서 뉴스 제목 링크 추출
    for item in soup.select("a[data-heatmap-target='.tit']"):
        href = item.get("href")
        title = item.get_text(strip=True)
        if href and title:
            news_links.append({"title": title, "url": href})

    # 이전 방식 실패 시 대체 선택자 사용
    if not news_links:
        for item in soup.select("a.news_tit"):
            title = item.get("title") or item.get_text(strip=True)
            href = item.get("href")
            if href and title:
                news_links.append({"title": title, "url": href})

    return news_links


def parse_article_content(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "html.parser")
    content_blocks = soup.select(
        "#dic_area, div#newsct_article ._article_body_contents, div.article_body > p, div#newsct_article p"
    )
    paragraphs = [block.get_text(strip=True) for block in content_blocks if block.get_text(strip=True)]
    return "\n".join(paragraphs).strip()


def main() -> None:
    search_url = (
        "https://search.naver.com/search.naver"
        "?where=nv&sm=top_sug.pre&fbm=0&acr=1&acq=%EB%B0%98%EB%8F%84%EC%B2%B4&qdt=0&ie=utf8&query=%EB%B0%98%EB%8F%84%EC%B2%B4&ackey=zi6yrkqg"
    )

    search_html = fetch_html(search_url)
    results = parse_search_results(search_html)

    if not results:
        print("뉴스 기사 링크를 찾지 못했습니다.")
        return

    print("검색 결과 뉴스 기사:")
    for idx, item in enumerate(results[:5], start=1):
        print(f"{idx}. {item['title']}")
        print(f"   {item['url']}")

    first_article = results[0]
    print("\n첫 번째 기사 크롤링 중:", first_article["title"])
    article_html = fetch_html(first_article["url"])
    article_text = parse_article_content(article_html)

    if article_text:
        print("\n=== 기사 본문 ===")
        print(article_text)
    else:
        print("기사 본문을 추출하지 못했습니다.")


if __name__ == "__main__":
    main()
