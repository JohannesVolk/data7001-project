from pathlib import Path
import imageio
import tempfile
import os
import shutil
from PIL import Image
from util import *

def make_video(image_list: list, fps: int, delete_folder=True, play_video=False):
    """The main def for creating a temporary video out of the 
    PIL Image list passed, according to the FPS passed
    Parameters
    ----------
    image_list : list
        A list of PIL Images in sequential order you want the video to be generated
    fps : int
        The FPS of the video
    delete_folder : bool, optional
        If set to False, this will not delete the temporary folder where images and video are saved, by default True
    play_video : bool, optional
        If set to false, the video generated will not be played, by default True
    """
    # Make an empty directort in temp, which we are gonna delete later
    dirpath = tempfile.mkdtemp()  # Example: '/tmp/tmpacxadh7t'
    video_filenames = []
    for i, each_image in enumerate(image_list):
        # TODO: Correct the below snippet
        # if not isinstance(each_image, type(Image)):
        #     raise Exception("The element is not an PIL Image instance")
        filename = "{}/{}.png".format(dirpath, i)
        video_filenames.append(filename)
        each_image.save("{}".format(filename))
    writer = imageio.get_writer("{}/test.mp4".format(dirpath), fps=fps)
    for each_image in video_filenames:
        writer.append_data(imageio.imread(each_image))
    writer.close()
    if play_video:
        os.system("vlc {}/test.mp4 vlc://quit".format(dirpath))
    else:
        print("Find your images and video at {}".format(dirpath))
        
    return dirpath


def image_mapper(path):
    image = convert_radar_colormap(imageio.imread(path))
    image_base = cv2.imread("data/base_observationwindow.png")[:, :, ::-1]
    image_base = cv2.resize(image_base, (512, 512), interpolation=cv2.INTER_LINEAR)
    image = cv2.addWeighted(image_base, 0.3, image, 0.6, 0)
    image = Image.fromarray(image)
    return image


s = make_video([image_mapper(path) for path in Path("output/weather").iterdir() if "jpg" in str(path) and "radar" in str(path)], fps = 5)

shutil.move(s + "/test.mp4", "demo/weather.mp4")
