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

from src.tuftg import tuftg

@click.command()
@click.option("--file", prompt="image in?", help="svg to process")
@click.option("--folder", default="img_output", help="folder to output into")
@click.option("--feed", default=100, help="set the speed of the machine when tufting")
@click.option("--colours", default=4, help="number of colours (yarn) ")
@click.option("--width", default=150, help="maximum bed width (x)")
@click.option("--height", default=150, help="maximum bed height (y)")
@click.option("--depth", default=3.8, help="maximum depth (z)")
@click.option("--spacing", default=0.25, help="space between tufting lines (inches)")
@click.option("--seed", default=0, help="random seed")
@click.option("--loglevel", default="INFO", help="set the log level.")
def run(
    folder,
    file,
    feed,
    colours,
    width,
    height,
    depth,
    spacing,
    seed,
    loglevel
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

    cmd = f"{imconvert} {file} +dither -colors {colours} -resize {width}x{height} reduce-colour-{colours}.png"
    log.debug(cmd)
    subprocess.run(cmd.split())

    img = cv2.imread(f"reduce-colour-{colours}.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    colors = np.where(hist>5000)

    img_number = 0
    for color in colors[0]:
        log.debug(f"working on color: {color}")
        split_image = img.copy()
        split_image[np.where(gray != color)] = 0
        cv2.imwrite(str(img_number)+".png",split_image)
        
        cmd = f"{imconvert} {img_number}.png -channel RGB -white-threshold 1% c-{img_number}.png"
        subprocess.run(cmd.split())

        fname = f"{os. getcwd()}/c-{img_number}.png"
        outputfile = tuftg(fname, depth, spacing, feed)

        log.info(f"gcode: /nc_output/{outputfile}")
        img_number+=1

    plt.hist(gray.ravel(),256,[0,256])
    plt.savefig('plt')

    log.debug("done.")

if __name__ == "__main__":
    run()
