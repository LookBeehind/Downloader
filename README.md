# Youtue Video Downloader 3000

1. pip install -r .\requirements.txt
2. You will also need to install ffmpeg and specify the bin folder location in "downloader.py" - https://github.com/BtbN/FFmpeg-Builds/releases

![img.png](assets/img_2.png)

Link specification: 

Simple YouTube video URL will download the video.

Link to a video within a playlist - will download 100 videos from the playlist.

Link to a playlist will download the whole playlist.

![img.png](assets/img.png)

If you don't specify the Download Options, it will be downloaded by its defaults, in to your "Downloads" folder.

By Selecting "Video + Audio", you can get the original video, or you can select "Video" - with no audio, or "Audio" - with no video.

Your settings will be saved in a XML document, so you can download a video multiple times, without specifying the properties each time, or you can switch the radio button, to set other properties.

![img.png](assets/img_1.png)

If a video is not getting downloaded, ensure that the resolution you selected is not too low, and it is actually available for that video.