import os

import moviepy.editor as mp
import numpy as np

# Get the directory path of the current Python file
current_directory = os.path.dirname(os.path.abspath(__file__))

# Concatenate the directory path with the PNG image file name
watermark = os.path.join(current_directory, 'watermark.png')

def video_watermark(video_file, output_path):
    video = mp.VideoFileClip(video_file)

    logo = (mp.ImageClip(watermark).set_duration(video.duration))

    fnl = mp.CompositeVideoClip([video, logo])
    print("-----------------> Processing.......")
    fnl.subclip(0).write_videofile(output_path)
    return True