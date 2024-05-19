# route-optimization-tool

This repository houses an application designed to survey rural transport routes. It leverages the capabilities of ArcPy to create optimized routes based on various geographic and logistic parameters.

## Instructions

### Install

#### Step 1: Install requirements.txt
To run the code, you need to have ArcPy installed. ArcPy is essential for performing geographic data analysis and creating routes. Follow the instructions in requirements.txt to set up ArcPy on your computer.

#### Step 2: Install Anaconda
Download and install Anaconda from the following link:
[Anaconda Download](https://www.anaconda.com/download/)

#### Step 3: Install Python 3.9 or 3.10
ArcPy requires Python 3.9 or 3.10, not higher. Follow these instructions to install Python 3.9 with Conda:
[How to Install Python 3.9 with Conda](https://saturncloud.io/blog/how-to-install-python-39-with-conda-a-guide-for-data-scientists/)

#### Step 4: Install ArcPy
After setting up Anaconda and Python, install ArcPy using the Anaconda prompt. Note that ArcGIS Pro must be installed on your computer.

Open Anaconda prompt and type the following command:
```bash
conda install arcpy=3.1 -c esri
```

#### Step 5: Run Code Files
To execute the Python scripts, use the `propy.bat` file provided by ArcGIS Pro. Replace `*path*.py` with the path to your script.

```bash
c:\Progra~1\ArcGIS\Pro\bin\Python\scripts\propy.bat *path*.py
```

### Additional Resources
- [Anaconda Download](https://www.anaconda.com/download/)
- [Saturn Cloud | #1 Rated ML Platform](https://saturncloud.io)