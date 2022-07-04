# path-annotator
Tool for manually-annotating trajectories during defensive behaviors and subsequent feature extraction, analysis, and visualization.

## Usage Instructions

1. Generate timing data
2. Run the script and link timing data

* 1.1 Select video and adjust display
* 1.2 Identify arena corners
* 1.3 Annotate trials

3. Repeat 1.1-1.3 for as many videos as desired.

### Generate timing data

![](https://github.com/kpc-simone/dmbs-tracking/blob/main/docs/keytimings.png)

### Run the script and link timing data

```
python annotate_position_loop.py 500 300
```

Dialog windows will prompt you to select
1. CSV file containing trial key timings, as specified above

### Select video and adjust display

The script will next prompt you to select the video for which to annotate trial paths followed by the animal. You will then be prompted to enter (in order) 1. the name of the animal associated with the video you loaded (as it appears in the spreadsheet) and 2. the test day. These inputs will be used to identify the relevant spreadsheet rows as well as the relevant video frames to annotate. For example, to annotate animal m1015 on test day 1:

![](https://github.com/kpc-simone/dmbs-tracking/blob/main/docs/userinput.png)

Next, you'll be able to modify some display settings. First, use the `LEFT` and `RIGHT` arrow keys to rotate the frame for labelling. The frame rotation must be such that the arena's width and depth correspond with the frame's x- and y- dimensions, respectively. For example, a 300 mm width, 500 mm depth arena should appear like this. 

![](https://github.com/kpc-simone/dmbs-tracking/blob/main/docs/rotation.png)

When satisfied, press `ESC` to go to the next step.

Use the `UP` and 'DOWN' arrows keys to adjust the brightness of the display, if necessary. Press `ESC` if when satisfied or to skip this step.

Finally, select the corners of the rectangular arena in the exact order requested (back left, back right, front right, front left). 

### Annotate trials

You can now start labelling the animal's position! Left click on the animal's nose and then tail. Once the script has received two points, it will display the next frame for annotation. The animal's previous position will be overlaid on the current frame. Nose is red, tail is blue:

![](https://github.com/kpc-simone/dmbs-tracking/blob/main/docs/labelling.png)

Keep left clicking the animal's nose,tail as it navigates around the arena with successive frames. The keyboard controls below can be used to speed up or slow down the labelling process depending on the animal's behavior. 

Keyboard controls:
```
1-8 	Number of frames to skip labelling 
` 	Go back N frames and relabel
`TAB`	Skip N frames
```


Trails of the animal's historical position will appear as you progress with labelling, and a progress bar is displayed in the command terminal to estimate time remaining for that trial.
![](https://github.com/kpc-simone/dmbs-tracking/blob/main/docs/labelling2.png)

When complete, the trial data will be saved in the`annotated-paths` folder. The script will generate a visualization of the animal's trajectory. 








