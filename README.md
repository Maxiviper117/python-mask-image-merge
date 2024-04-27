
# Image Mask Merger Tool

This tool is a GUI application built with Python and Tkinter that allows you to merge images with corresponding masks, creating new images with a black background for the non-masked areas.

## Features

- Browse and select directories for input images, masks, and output
- Automatically process all images and masks in the selected directories
- Save settings for input and output directories between sessions
- Real-time logging to monitor the progress and status of the merging process
- Stop button to cancel the current processing operation

## Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- Tkinter

## Installation

1. Clone the repository using Git:

```bash
git clone https://github.com/Maxiviper117/python-mask-image-merge.git
```

2. Install the required dependencies:

```bash
pip install opencv-python numpy
```

Note: Tkinter is usually included with Python installations by default.

## Usage

1. Run the `image_mask_merger.py` script to launch the GUI application.
2. Click the "Browse" buttons to select the directories for input images, masks, and the output location.
3. Click the "Merge Images and Masks" button to start the merging process.
4. Monitor the progress in the log console.
5. If needed, click the "Stop Processing" button to cancel the current operation.

The merged images will be saved in the specified output directory with a `_black_background.png` suffix.

## Notes

- The application expects input images with the `.JPG` extension and masks with the `.mask.png` extension.
- The masks should be grayscale images with white (255) pixels representing the masked areas and black (0) pixels for the background.
- The dimensions of the input image and its corresponding mask must match for successful merging.

## License

This project is licensed under the [MIT License](LICENSE).
