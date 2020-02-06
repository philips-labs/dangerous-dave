# This is a demo app vo presenting video with API to identify current emotion on the frame

In requirements there is also algorithmia package, but most probable is that will fail to install itself as it is not connected to the package managers.
You will need to enter your environment via a shell and run '`pip install algorithmia`' - this is the proper way to install it

We are using algorithmia from pip and pysimplegui and opencv packages
## Installation of project
To use the environment, type
```
conda env create -f environment.yml
conda activate demo_py_app
```

To update the environment when environment.yml is changed or packages are updated,
```
conda env update -f environment.yml
conda activate demo_py_app
```
