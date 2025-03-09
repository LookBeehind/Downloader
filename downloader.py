import yt_dlp


def on_progress(d):
    if d['status'] == 'finished':
        print('Download complete!')


def download(url, path, video_resolution=1080, ext='Default', form='Video + Audio'):
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False, process=False)
        if 'entries' in info_dict:
            for entry in info_dict['entries']:
                ydl.download([entry['url']])
        else:
            ydl.download([url])
