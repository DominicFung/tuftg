from loguru import logger as log
import click

import cv2
import numpy as np
from matplotlib import pyplot as plt

import sys
import random
import ntpath
import os
import subprocess
from shutil import copyfile

from src.tuftg import TuftG

@click.command()
@click.option("--file", prompt="image in?", help="svg to process")
@click.option("--folder", default="img_output", help="folder to output into")
@click.option("--feed", default=2540, help="set the speed of the machine when tufting")
@click.option("--colours", default=4, help="number of colours (yarn) ")

@click.option("--width", default=150,   help="set image width  (x) in pxs. Image will be scaled (up or down) to the desired resolution. Each px is 5mms of travel. You can set this to a different value using --pxs.")
@click.option("--height", default=150,  help="set image height (y) in pxs. Image will be scaled (up or down) to the desired resolution. Each px is 5mms of travel. You can set this to a different value using --pxs.")
@click.option("--pxs", default=5,       help="sets mm/px. For example: a 150 x 150 image will travel 750mm in the x direction and 750 in the y direction.")

@click.option("--bed_width", default=812.8,  help="set the maximum working area in x direction. You can find this value by jogging the maching to the right most point. This value is in mm.")
@click.option("--bed_height", default=812.8, help="set the maximum working area in y direction. You can find this value by jogging the maching to the left most point. This value is in mm.")
@click.option("--tuft_x_offset", default=10, help="the distance (in mm), the tufting needle is to the right or left of where the mill would be. This is useful in the case that the tufting gun cannot fit in the milling machine hole and needs to be mounted on the side. Will modify the max bed_width accordingly.")
@click.option("--tuft_y_offset", default=0,  help="the distance (in mm), the tufting needle is to the up or down of where the mill would be. This is useful in the case that the tufting gun cannot fit in the milling machine hole and needs to be mounted on the side. Will modify the max bed_width accordingly.")

@click.option("--depth", default=110.1944, help="minimum depth (z), this is in mm.")                                              # was 3.236
@click.option("--max_depth", default=132.9944, help="maximum depth (z), to account for the stretch of material, this is in mm")   # was 5.236
@click.option("--spacing", default=0.25, help="space between tufting lines (mm)")
@click.option("--seed", default=0, help="random seed")
@click.option("--loglevel", default="INFO", help="set the log level.")
def run(
    file, folder, feed, colours,
    width, height, pxs,
    bed_width, bed_height, tuft_x_offset, tuft_y_offset,
    depth, max_depth, spacing,
    seed,loglevel
):
    random.seed(seed)
    imconvert = "convert"

    if folder != ".":
        try:
            os.mkdir(folder)
        except:
            pass

    foldername = os.path.join(folder, ntpath.basename(file) + ".img2gcode")
    try:
        os.mkdir(foldername)
    except:
        pass

    copyfile(file, os.path.join(foldername, ntpath.basename(file)))

    log.remove()
    log.add(sys.stderr, level="INFO")
    log.add("file.log", level=loglevel)

    log.info(f"working in {foldername}")
    log.debug(foldername)
    os.chdir(foldername)
    file = ntpath.basename(file)

    cmd = f"{imconvert} {file} +dither -colors {colours} -resize {width}x{height} -morphology Close Diamond -morphology Erode Diamond reduce-colour-{colours}.png"
    log.debug(cmd)
    subprocess.run(cmd.split())

    img = cv2.imread(f"reduce-colour-{colours}.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])

    hist_flat = hist.flatten()
    colors = np.argsort(hist_flat)[-colours:] # get the x largest colours.
    log.info(f"colors: {colors}")

    img_number = 0
    for color in colors:
        log.debug(f"working on color: {color}")
        split_image = img.copy()
        split_image[np.where(gray != color)] = 0
        cv2.imwrite(str(img_number)+".png",split_image)
        
        cmd = f"{imconvert} {img_number}.png -channel RGB -white-threshold 1% c-{img_number}.png"
        subprocess.run(cmd.split())

        fname = f"{os. getcwd()}/c-{img_number}.png"

        tg = TuftG(im_name=fname, pxs=pxs, feed=feed,
                  bed_width=bed_width, bed_height=bed_height, tuft_x_offset=tuft_x_offset, tuft_y_offset=tuft_y_offset,
                  depth=depth, max_depth=max_depth, spacing=spacing)
        
        outputfile = tg.convert_img()
        log.info(f"images: {folder}/{foldername}/c-{img_number}.png")

        tg.write_gcode()
        log.info(f"gcode: folder/{foldername}/nc_output/{outputfile}")
        img_number+=1

    plt.hist(gray.ravel(),256,[0,256])
    plt.savefig('plt')

    log.debug("done.")

if __name__ == "__main__":
    run()
