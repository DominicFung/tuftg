# TuftG

TuftG is a GCode generator for your CNC machine turned rug maker. It takes an image, separates the image into several black/white images (based on original image colour) and turns that into gcode. Unlike other milling machine gcodes, there is no curvature or roughing passes. It moves rapidly from one tuft starting point to another, making sure it moves up vertically first (to clear the needle) before moving to the next point.

<img src="https://github.com/DominicFung/tuftg/blob/main/images/monstera-leaf-vector-16307990.jpg?raw=true" align="center"
     alt="Screenshot of Logistical.ly" width="200" height="200">
<span style="font-size:5em;padding-left:20;padding-right:10;padding-top:80"> → </span>
<img src="https://github.com/DominicFung/tuftg/blob/main/instructions/screenshots/screenshot1.png?raw=true" align="center"
     alt="Screenshot of Logistical.ly" width="300" height="200">


## Limitations

Currently, it is used to convert my Onefinity CNC into a tufting machine. It uses M7 and M9 to turn on and off the tufting gun, which will require you to buy / 3D print adaptors on your own. I've added the adaptor designs for the Onefinity here in this repo as STL files. The parts are also listed in the instruction's folder!

It also only tufts horizontally. Probably lots of cleaver engineering to make it do outlines and tuft like a human.

## Usage

```
python3 main.py --file images/monstera-leaf-vector-16307990.jpg --colours 2 --width 150 --height 150
```

gcode is located in `img_output/<name of image>/nc_output/`