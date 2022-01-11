""" Run to convert the images of the last run into a .gif. """

import glob
import os
import imageio


FRAME_DURATION = 0.3

list_of_folders = glob.glob('./runs/*')
latest_folder = max(list_of_folders, key=os.path.getctime)
print(latest_folder)

filenames = sorted(os.listdir(latest_folder), key=lambda x: int(x[:-4]))
print(filenames)
images = []
for filename in filenames:
    images.append(imageio.imread(latest_folder + '/' + filename))
imageio.mimsave('demo.gif', images, duration=FRAME_DURATION)