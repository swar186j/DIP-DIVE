from flask import Blueprint, render_template,session, send_file, request, Response, jsonify
from flask_login import login_required, current_user
from __init__ import create_app, db
import os
from chat import get_response
import pandas as pd
#from dipdive import textclassification
from supportFile import get_frame, get_score
from textclassification import *
import datetime
from flask_login import login_required, current_user
from twilio.rest import Client


account_sid = "your_twilio_id"
auth_token = "your_auth_token"
client = Client(account_sid, auth_token)

vid_dep=0
speech_dep=0
text_dep=0
# our main blueprint
main = Blueprint('main', __name__)

#create app
app = create_app() # we initialize our flask app using the create app

#define routes
# home page that return 'index'
@main.route('/') 
def index():
    return render_template('index.html')

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    if len(text) > 100:
        message = {"answer": "I'm sorry, your query has too many characters for me to process. If you would like to speak to a live agent, say 'I would like to speak to a live agent'"}
        return jsonify(message)
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)
    
# depression detection using textual data
@main.route('/text',methods=['GET', 'POST'], endpoint='text')
@login_required
def text():
    global text_dep
    import textclassification 
    if request.method == 'POST': 
        email=current_user.email
        session['mail'] = email
        num=current_user.mobile
        t_symptoms= request.form["symptoms"]
        t_result= textclassification.predict(t_symptoms,email,num)
        
        if(t_result.split(':')[0] == 'Depression Detected'):
            text_dep=1
        else:
            text_dep =0
        session['text_dep'] = text_dep

        session['tres']= t_result
        session['tsym'] = t_symptoms
        print(text_dep)
        return render_template('text.html',email=email,symptoms=t_symptoms,result=t_result)
        
    return render_template('text.html')


# depression detection using audio 
@main.route('/audio',methods=['GET', 'POST'], endpoint='audio')
@login_required
def audio():
    global speech_dep
    import textclassification
    if request.method == 'POST':
        global a_result, a_symptoms
        a_symptoms = request.form["symptoms"]
        
        email=current_user.email
        print(email)
        num=current_user.mobile
        a_result= textclassification.predict(a_symptoms,email,num)
        if(a_result.split(':')[0] == 'Depression Detected'):
            speech_dep=1
        else:
            speech_dep=0
        
        session['speech_dep']= speech_dep

        
        session['ares']= a_result
        session['asym'] = a_symptoms
        
        return render_template('audio.html',email=email,symptoms=a_symptoms,result=a_result)
    return render_template('audio.html')


# depression detection using visual data
@main.route('/video',methods=['GET', 'POST'], endpoint='video')
@login_required
def video():
    return render_template('video.html')

#stream video
@main.route('/video_stream',methods=['GET', 'POST'], endpoint='video_stream')
@login_required
def video_stream():
    num=current_user.mobile
    return Response(get_frame(num),mimetype='multipart/x-mixed-replace; boundary=frame')
    
@main.route('/video_result',methods=['GET', 'POST'])
@login_required
def video_result():  
    v_result=get_score()
    if(v_result == 'Depression Detected.'):    
        vid_dep = 1       
    else:
        vid_dep = 0
    session['vid_dep']= vid_dep
    print(v_result)
    session['vres']= v_result
    return render_template('video_result.html',result=v_result)



@app.route('/final_result', methods=['GET', 'POST'])
def final_result():
    text_dep = session['text_dep']
    
    speech_dep = session['speech_dep']
    vid_dep = session['vid_dep']
    num=current_user.mobile
    
    depression = "Video Depression = "+str(vid_dep) + "," + "Text Mining Depression = "+str(text_dep)+","+"Speech Depression = "+str(speech_dep)
    print(depression)
    score = ((vid_dep+speech_dep+text_dep)/3)*100

    if score > 66:
        score='High depression'
        
        message = client.messages \
        .create(
        	 body = " Refer: https://www.youtube.com/watch?v=2UtwSI7lgkQ Please visit the experts section in Dip-dive and contact doctors immediately!",
        	 from_='+18647321527',
        	 to="+91"+str(num)
        )
        
        
    elif score > 33:
        score ='Mild depression'
        
        message = client.messages \
        .create(
        	 body = " https://www.youtube.com/watch?v=2UtwSI7lgkQ Please visit this link: https://coreartry.blogspot.com/2022/04/dip-dive.html",
        	 from_='+18647321527',
        	 to="+91"+str(num)
        )
        
        
    elif score < 33:
        score='No depression'
        
        

    else: 
        None

    return render_template('final_result.html',text_dep=text_dep, speech_dep= speech_dep, vid_dep=vid_dep,score=score)

#generate user history/report
@main.route('/set')
def set():
    import csv
    email=current_user.email    
    session['mail'] = email
    name= session['mail']
    last_seen = datetime.datetime.now()
    #check if text result exists
    if 'tres' in session:
        text_sym= session['tsym']
        text_res = session['tres']
    else:
        text_sym = None
        text_res = None

    #check if audio result exists
    if 'ares' in session:
        audio_res = session['ares']
        audio_sym= session['asym']
    else:
        audio_sym= None
        audio_res= None

    if 'vres' in session:
        video_res = session['vres']
    else:
        video_res= None
    
    
    header= ['Last_activity','Text_symptoms','Text_Result','Audio_symptoms','Audio_Result','Video_Result']
    data=[last_seen,text_sym, text_res,audio_sym,audio_res,video_res]
    import os.path
    file_path="./history/"+name+'-report.csv'
    #write result to file
    if os.path.exists(file_path) == False:
        with open(file_path, 'a', newline='') as csvfile:
            writer= csv.writer(csvfile)
            writer.writerow(header)
            writer.writerow(data)
    else:
        with open(file_path, 'a', newline='') as csvfile:
            writer= csv.writer(csvfile)
            writer.writerow(data)
    csvfile.close()
    session['file_'] = file_path 
    return send_file(file_path,as_attachment=True)

@main.route('/view')
def view_sheet():
    name= session['mail']
    view_file="./history/"+name+"-report.csv"
    data = pd.read_csv(view_file)
    return render_template('table.html', tables=[data.to_html()], titles=[''])

#about page
@main.route('/about', endpoint='about')
def about():
	return render_template('about.html')

#FAQ page
@main.route('/faq', endpoint='faq')
def faq():
	return render_template('faq.html')

#Contact page
@main.route('/contact', endpoint='contact')
def ContactUs():
	return render_template('contact.html')

#Terms and conditions
@main.route('/terms', endpoint='terms')
def terms():
	return render_template('terms.html')

#diagnose
@main.route('/diagnose', endpoint='diagnose')
def diagnose():
	return render_template('diagnose.html')

@main.route('/experts', endpoint='experts')
def experts():
	return render_template('experts.html')

@main.route('/que', endpoint='que')
def que():
	return render_template('que.html')


# profile page that return 'profile'
@main.route('/profile') 
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, id=current_user.id, email=current_user.email, mobile= current_user.mobile, age=current_user.age, city=current_user.city)

@main.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    #create the SQLite database
    db.create_all(app=create_app()) 
    # run the flask app on debug mode
    app.run(debug=True) 

