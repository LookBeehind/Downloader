import yt_dlp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def on_progress(d):
    if d['status'] == 'finished':
        print('Download complete!')


def is_playlist(url: str) -> bool:
    query = parse_qs(urlparse(url).query)
    return 'list' in query


def remove_list_param(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Remove 'list' and reconstruct the query
    query.pop('list', None)
    clean_query = urlencode(query, doseq=True)

    # Rebuild the full URL without 'list'
    clean_url = urlunparse(parsed._replace(query=clean_query))
    return clean_url


def download(
    url: str, path: str, video_resolution: int = 1080, ext: str = 'Default', form: str = 'Video + Audio'
) -> None:
    ffmpeg_loc = 'C:/ffmpeg/bin'
    # Common options across all formats
    common_opts = {
        'outtmpl': f'{path}/%(title)s.%(ext)s',
        'max_retries': 5,
        'download_archive': 'downloaded.txt',
        'progress_hooks': [on_progress],
    }

    if form == 'Video + Audio':
        ydl_opts = {
            'format': f'bestvideo[height<={video_resolution}]+bestaudio/best[height<={video_resolution}]',
            'ffmpeg_location': ffmpeg_loc,
        }
        if ext != 'Default':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': ext,
            }]
    elif form == 'Video':
        ydl_opts = {
            'format': f'bestvideo[height<={video_resolution}]',
        }
    else:  # Audio only
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': ffmpeg_loc,
        }

    ydl_opts.update(common_opts)

    if is_playlist(url):
        handle_playlist_url(ydl_opts, url)
    else:
        handle_non_playlist_url(ydl_opts, url)


def handle_non_playlist_url(ydl_opts: dict, url: str) -> None:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def handle_playlist_url(ydl_opts: dict, url: str) -> None:
    urls = get_urls(url)
    ydl_opts['no_playlist'] = True
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


def get_urls(url: str, headless: bool = False) -> list[str]:
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(2)

    SCROLL_PAUSE = 2
    prev_height = 0

    while True:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

    links = driver.find_elements(By.XPATH, "//a[@id='video-title']")
    # items_xpath = ("//div[@id='contents']/ytd-item-section-renderer[@header-style][1]/div[@id='contents']"
    #                "/ytd-playlist-video-list-renderer/div[@id='contents']/ytd-playlist-video-renderer"
    #                "/div[@id='content']/div[@id='container']/div[@id='meta']/h3//a/@href")

    urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
    formatted_urls = [remove_list_param(url) for url in urls if url]
    urls = [url for url in formatted_urls if url]  # filter out empty
    driver.quit()
    return urls


if __name__ == '__main__':
    video_url = 'https://www.youtube.com/playlist?list=PLYUcVkkLR4_4L9d1zeco0nPoH64qt5nNv'
    video_urls = get_urls(video_url)
