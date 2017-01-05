import os
from skimage import exposure, color, filters
from PIL import Image
import numpy as np



def parse_file_name(f):
    f = f.split('/')[-1]
    f = f.split('.')[0]
    f = f.split('_')
    speed = int(f[3])
    angle = int(f[5])
    #msecs = int(f[7])
    return angle, speed



def filter_session(session_path, speed_threshold = 200):
    """
    Get the paths to session images that are likely not before or after
    a crash. 
    """
    imgs = os.listdir(session_path)
    imgs.sort()

    split_imgs = [parse_file_name(i) for i in imgs]

    keep_index = [0 for _ in imgs]

    for i, x in enumerate(imgs):
        #remove images with speed < 200
        if split_imgs[i][1] < speed_threshold:
            keep_index[i]=0
        #remove the first and last 60 frames
        elif i < 60 or i > len(imgs) - 60:
            keep_index[i]=0
        else:
            keep_index[i]=1

    past_removed = 0
    for i, x in enumerate(imgs):
        #remove the 20 frames before an images with speed <threshold
        if 0 in keep_index[i: i+20]: 
            if keep_index[i] != 0:
                past_removed += 1
                keep_index[i]=0

    future_removed = 0
    for i, x in reversed(list(enumerate(imgs))):
        #remove the 20 frames after an image with speed <threshold
        if 0 in keep_index[i-20: i]: 
            if keep_index[i] != 0:
                future_removed += 1
                keep_index[i]=0

    print('total images: %s   kept:%s' %(len(imgs), sum(keep_index)))
    
    filtered_imgs = [img for i, img in enumerate(imgs) if keep_index[i] ==1 ]
    filtered_img_paths = [os.path.join(session_path, i) for i in filtered_imgs]
    return filtered_img_paths





def create_video(img_dir_path, output_video_path):

    # Setup path to the images with telemetry.
    full_path = os.path.join(img_dir_path, 'frame_*.png')

    # Run ffmpeg.
    command = ("""ffmpeg
               -framerate 30/1
               -pattern_type glob -i '%s'
               -c:v libx264
               -r 15
               -pix_fmt yuv420p
               -y
               %s""" % (full_path, output_video_path))
    response = envoy.run(command)
