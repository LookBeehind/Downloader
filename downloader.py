import os
from pytube.cli import on_progress
import yt_dlp

def on_progress(d):
    if d['status'] == 'finished':
        print('Download complete!')


def download(url, path, video_resolution=1080, ext='Default', form='Video + Audio'):

    ffmpeg_loc = 'C:/ffmpeg/bin'
    if form == 'Video + Audio':
        ydl_opts = {
            'format': f'bestvideo[height<={video_resolution}]+bestaudio/best[height<={video_resolution}]',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_loc,
            'max_retries': 5,
        }

        if ext != 'Default':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': ext,
            }]
    elif form == 'Video':
        ydl_opts = {
            'format': f'bestvideo[height<={video_resolution}]',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'max_retries': 5,
        }
    else:
        ydl_opts = {
            'format': f'bestaudio/best',
            'outtmpl': f'{path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': ffmpeg_loc,
            'max_retries': 5,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False, process=False)

        if 'entries' in info_dict:
            for entry in info_dict['entries']:
                ydl.download([entry['url']])
        else:
            ydl.download([url])


# download(url='https://www.youtube.com/watch?v=8V_B0hgDKU0=1', form='Video', video_resolution=2160)
