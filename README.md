# YouTube Video Downloader 3000

## Setup Instructions
1. `pip install -r .\requirements.txt`
2. You will also need to install ffmpeg and specify the bin folder location in `downloader.py`
   - https://github.com/BtbN/FFmpeg-Builds/releases
3. Update the `FFMPEG_LOC` const in `config.py` with the path to your `ffmpeg` bin folder.

## Usage Instructions
Run the `main.py` or the compiled exe file.

* If you don't specify the Download Options, it will be downloaded by its defaults,
  in to your `Downloads` folder (`C:\Users\<user>\Downloads`).
* By Selecting `Video + Audio`, you can get the original video, or you can select `Video` - 
  with no audio, or `Audio` - with no video.
* Your settings will be saved in an XML document, so you can download a video multiple times, 
  without specifying the properties each time, or you can switch the radio button, to set other properties.
* If a video is not getting downloaded, ensure that the resolution you selected is not too low,  
  and it is actually available for that video.

## Link specification: 

1. Simple YouTube video URL will download the video.
2. Link to a video within a playlist - will download 100 videos from the playlist.
3. Link to a playlist will download the whole playlist.

## Building the Executable
To build the exe file, use the following command:

```bash
pyinstaller --onefile --noconsole --icon=assets\icon.ico main.py
```

To use predefined playlist links, you can create a text file named `playlists.txt` in the same directory as the executable,
and add your playlist URLs there, one per line in the following format:

```csv
Main,https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID_1
Second,https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID_2
```

When you run the executable, it will read the `playlists.txt` file and populate the dropdown menu with the playlist names.