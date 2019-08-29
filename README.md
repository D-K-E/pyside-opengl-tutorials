# pyside-opengl-tutorials
Tutorials on the new QtGui based OpenGL api of PySide2


## Requirements

In the main folder which contains the `setup.py` execute the following
commands on the terminal.

- Create a virtual env with conda `conda create -n pyside-opengl-tuto`

- Activate your virtual env `conda activate pyside-opengl-tuto`

- Install python `conda install -c conda-forge python=3`

- Install `pyside2` and `shiboken2` `pip install PySide2==5.11 shiboken2==5.12`

- Install PyOpenGL_accelerate `conda install -c anaconda pyopengl-accelerate`

- Normally PyOpenGL_accelerate installation automatically installs the
  PyOpenGL, check this by verfying your list of packages `conda list`

- Setup the rest of the packages using pip `pip install .`


## Description

There are unfortunately not a lot of tutorials on using pyside2 for rendering
OpenGL.
This is simply a collection of tutorials on using PySide2 for rendering
opengl graphics.
If you are not an experienced user with opengl the code can be strange and
daunting at times due to low level nature of OpenGL though I try to 
comment as much as I can.
If you are an absolute beginner, I suggest you to follow at least the Getting Started section from the infamous `https://learnopengl.com/`

If you are somewhat experienced with opengl but just want to test PySide2 as
front end to it. These tutorials should give you a rough idea about how to
initialize GL, how to render your drawing loop, as well as passing data to
your scene like textures or keystrokes etc.

The first tutorial `triangle` is heavily commented, the rest of them simply
points out differences with respect to c/c++ or to other tutorials.

The tutorials are linear in nature, so you can use it alongside with 
other learning ressources for OpenGL.

If you feel like you can contribute to tutorials, they are always welcomed.


## List of Tutorials

As stated in the description the list is progressive.

1. [Hello Triangle](./tutorials/01-triangle/TriangleTutorial.ipynb)
2. [Rectangle](./tutorials/02-rectangle/RectangleTutorial.ipynb)
3. [Multiple VAO-VBO couples](./tutorials/03-VaoVbo/VAOsVBOs.ipynb)
4. [Render an Image - Texture](./tutorials/04-texture/TextureTutorial.ipynb)
5. [Hello Cube - 3D rendering](./tutorials/05-cube/CubeTutorial.ipynb)
5. [Event Handling](./tutorials/06-events/EventsTutorial.ipynb)
