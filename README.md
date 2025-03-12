# Image Sorter


### Description
Image Sorter is a terminal-based image management tool built using Python and curses. It allows users to efficiently sort, move, rename, delete images from a specified directories using keyboard shortcuts.


### Features
- **File Navigation**: Scroll through images using arrow keys.
- **Image Display**: Uses *kitty icat* to preview images in the terminal.
- **Sorting & Moving**: Move files to predefined directories with numeric shortcuts.
- **File Management**: Rename and delete images.


### Installation

##### Prerequisites
- Python 3.x
- kitty terminal (for image preview with icat)

##### Clone Repository
To install and run this project, follow these steps:
```
$ git clone https://github.com/yevhen-martynenko/python-image-sorter.git
$ cd image-sorter
```


### Usage

![How the Image Sorter Works](assets/how-to-use-image-sorter.mp4)


##### Running the Application
```
$ python main.py --input-dir <path-to-images> --output-dirs <dir1> <dir2> ...
$ python main.py -i <path-to-images> -o <dir1> <dir2> ... 
```

##### Command Line Arguments
Run `python main.py --help` for a detailed help message.

| Argument      | Short Argument | Description                                  |
| ------------- | -------------- | ---------------------------------------------|
| --input-dir   | -i             | Path to the directory containing images      |
| --output-dirs | -o             | List of target directories for sorting       |
| --auto-rename | -r             | Automatically rename files after moving them |
| --copy-mode   | -c             | Copy files instead of moving them            |

##### Key Bindings
Press F1 in the app to open the help menu.

| Key          | Action                        |
| ------------ | ----------------------------- |
| ↓ / j        | Move down                     |
| ↑ / k        | Move up                       |
| 1-9, 0       | Move to directories 1-10      |
| ALT + 1-9, 0 | Move to directories 11-20     |
| \` + 1-9, 0  | Move to directories 21-30     |
| DEL / d      | Delete image                  |
| F2 / r       | Remove image                  |
| F1 / h       | Open help menu                |
| ENTER        | Open image with system viewer |
| q            | Quit application              |


### Contributing
Contributions are welcome! Feel free to submit issues or pull requests.


### License
This project is licensed under the MIT License. See LICENSE for details.
