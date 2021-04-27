# Manometry WepApp

A web application to deploy a YOLOv5 object detection model to detect and classify Colonic Motor Patterns in manometry data. It was built using the *python-flask* framework. 


## Installing the  WebApp

### Prerequisites
Python will need to be installed before running this Web App. To check if Python is already installed, type `python --version` in a Command Prompt. If no version is reported then install Python from [here](https://www.python.org/downloads/). 

Preferably, install in a virtual environement. If virtualenv is not already installed (check using `virtualenv --version`) then install using `pip install virtualenv` in a Command Prompt  


```shell
# 1. Clone the repo and cd to the project directory
$ git clone https://github.com/secdean/manometry.git
$ cd manometry

# 2. Create a virtual environment and activate it. This is where dependencies for the project will be installed. 
$ virtualenv -p python3 venv
$ source venv/bin/activate

# 4. Install the necessary packages using:
$ pip install -r requirements.txt

```


## How to use
```shell
# 1. Open a Command Prompt and run: 
$ python app.py

# 2. Open an internet browser with the URL: 
http://localhost:5000

# 3. Upload files: 
# 10-minute contour plots or 
# CSV files of raw sensor data

```

## Examples

<p align="center">
  <img src="https://github.com/secdean/manometry/blob/main/static/webapp_2.png" height="400px" width="760px" alt="">
</p>


- **4-label model**

<p align="center">
  <img src="https://github.com/secdean/manometry/blob/main/static/inference/005261_3_8_cont.png" height="380px" alt="">
  <img src="https://github.com/secdean/manometry/blob/main/static/inference/005245_3_22_cont.png" height="380px" alt="">
</p>


- **2-label model**

<p align="center">
  <img src="https://github.com/secdean/manometry/blob/main/static/inference_2/005261_3_8_cont.png" height="380px" alt="">
  <img src="https://github.com/secdean/manometry/blob/main/static/inference_2/005245_3_22_cont.png" height="380px" alt="">
</p>


------------------
