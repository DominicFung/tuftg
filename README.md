# TuftG

Tuft G is a GCode generator. It takes an image, separates the image into several black/white images (based on original image colour) and turns that into gcode. Unlike other milling machine gcodes, there is no curvature or roughing passes.

## Limitations

Currently, it is used to convert my Onefinity CNC into a tufting machine. It uses M7 and M9 to turn on and off the tufting gun.

It also only tufts horizontally. 

## Usage

```
python3 img2gcode.py --file images/monstera-leaf-vector-16307990.jpg --colours 2 --width 150 --height 150
```

gcode is located in `img_output/<name of image>/nc_output/`