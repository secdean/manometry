import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
# from flask_table import Table, Col
from werkzeug.utils import secure_filename
import subprocess
import pathlib
import events_4labels
import events_2labels
from main import make_plots

events_dict = {}
events_dict_2 = {}  

app=Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

# Get current path
path = os.getcwd()

# paths to uploaded and processed files
UPLOAD_FOLDER = os.path.join(path, 'uploads')
PROCESS_FOLDER = os.path.join(path, 'inference')

# Make uploads directory if it doesn't exist
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extension for upload files
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# home page
@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # if a csv file has been uploaded then run make_plots to generate segmented contour plots 
                if filename.endswith(('csv','CSV')):
                    print('Uploaded CSV file {}'.format(filename))
                    print('Making plots...')
                    make_plots(cont=0, 
                               sens=0, 
                               water=0, 
                               individual_sens=0,
                               check_butter=0,
                               anus=0,
                               segmented=1,
                               csv_dir=app.config['UPLOAD_FOLDER'])
                    print('Finished making plots')
        flash('Images uploaded', 'info')
        return redirect('/')


# inference using 4-label model
@app.route('/process')
def process():
    global events_dict 
    # detect.py runs inference on images in upload directory
    # output is: images with bounding boxes overlaid and .txt files of bound box details
    subprocess.call(['python', 'models/yolov5/detect.py',
                     '--weights', 'models/weights/best_4labels.pt',    
                     '--img', '864',
                     '--conf', '0.4',
                     '--source', 'uploads',
                     '--output', 'static/inference',
                     '--save-txt',
                     '--save-conf'])
    # events_4labels reads bound box .txt files, extracts various stats and writes to dictionary
    events_dict = events_4labels.events_stats(os.path.join(path, 'static/inference/*.txt'))
    print(events_dict)
    files = os.listdir(os.path.join(path, 'static/inference'))
    return redirect(url_for('results_2'))


# inference using 2-label model
@app.route('/process_2')
def process_2():
    global events_dict_2 
    # detect.py runs inference on images in upload directory
    # output: images with bounding boxes overlaid and .txt files of bound box details
    subprocess.call(['python', 'models/yolov5/detect.py',
                     '--weights', 'models/weights/best_2labels.pt',    
                     '--img', '864', 
                     '--conf', '0.4',
                     '--source', 'uploads',
                     '--output', 'static/inference_2',
                     '--save-txt',
                     '--save-conf'])
    # events_2labels reads bound box .txt files, extracts various stats and writes to dictionary
    events_dict_2 = events_2labels.events_stats(os.path.join(path, 'static/inference_2/*.txt'))
    print(events_dict_2)
    files_2 = os.listdir(os.path.join(path, 'static/inference_2'))
    return redirect(url_for('results_3'))


# results of 4-label model 
@app.route('/results_2/')
@app.route('/results_2/<fname>')
def results_2(fname = None):
    global events_dict 
    # list all the filenames in inference dir with .png extension
    ext = ['.png', '.jpg', '.jpeg']
    files = [f for f in os.listdir(os.path.join(path, 'static/inference')) if f.lower().endswith(tuple(ext))]
    # when first loading page, it will have no fname so just pick first in list for loading
    if not fname:
        print('loading first time')
        fname = files[0]
    print(fname)
    #print(events_dict[fname[:-4]+'.txt'])           # write dictionary info on key fname[:-4]
    if not events_dict:
        events_dict = events_4labels.events_stats(os.path.join(path, 'static/inference/*.txt'))
    # write dictionary info on key fname[:-4] to var ind_events
    fname_key = fname[:-4]+'.txt' 
    print('fname_key is ' + str(fname_key))
    if fname_key in events_dict:
        print('*********** present in dict ******************')
        ind_events = events_dict[fname[:-4]+'.txt']  
    else:
        print('****************  not in dict  ****************')
        ind_events = {0:{1: 'no', 2: 'events'}}    
    # pass: list of filesnames (no ext), current filename fname, dict contents for fname.
    return render_template('results_2.html', files=files, fname = fname, ind_events = ind_events)    


# results of 2-label model
@app.route('/results_3/')
@app.route('/results_3/<fname_2>')
def results_3(fname_2 = None):
    global events_dict_2 
    # list all the filenames in inference dir with .png extension
    ext = ['.png', '.jpg', '.jpeg']
    files_2 = [f for f in os.listdir(os.path.join(path, 'static/inference_2/')) if f.lower().endswith(tuple(ext))]
    # when first loading page, it will have no fname so just pick first in list for loading
    if not fname_2:
        print('loading first time')
        fname_2 = files_2[0]
    print(fname_2)
    #print(events_dict_2[fname[:-4]+'.txt'])           # write dictionary info on key fname[:-4]
    if not events_dict_2:
        events_dict_2 = events_2labels.events_stats(os.path.join(path, 'static/inference_2/*.txt'))

    # write dictionary info on key fname[:-4] to var ind_events 
    fname_2_key = fname_2[:-4]+'.txt' 
    print('fname_2_key is ' + str(fname_2_key))
    if fname_2_key in events_dict_2:
        print('*********** present in dict ******************')
        ind_events_2 = events_dict_2[fname_2[:-4]+'.txt']  
    else:
        print('****************  not in dict  ****************')
        ind_events_2 =  {'no':{1: 'events'}} 
    # pass: list of filesnames (no ext), current filename fname, dict contents for fname.
    return render_template('results_3.html', files_2=files_2, fname_2 = fname_2, ind_events_2 = ind_events_2)    


if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000,debug=True,threaded=True)





