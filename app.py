from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "NFAQJQL"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

#Variables available outside the scope of the exisitng routes. 
title = satisfaction_survey.title
length = len(satisfaction_survey.questions)

RESPONSE = "responses"
previous_id = None

@app.route('/')
def home_route():
    """Initialize the home template with basic title and button to start the survey"""

    return render_template('home.html', title=title)


@app.route('/start', methods=["POST"])
def start():
    """Clear previous instance of Response whenever a user clicks the start survey button."""
    session[RESPONSE] = []
    session["redirect"] = 1
    session["previous_id"] = None
    
    return redirect("/survey/1")

@app.route('/survey/<q_id>')
def q_maker(q_id):
    """Logic to execute when a proper q_id is passed and is within the boundaries of the given 'length'.
    Furthermore, prevent the user from jumping to the next question when the current question is not answered."""

    if int(q_id) >= 1 and int(q_id) <= length:
        if len(session[RESPONSE])+1 == int(q_id):
            status = f"Question {q_id}"

            question = satisfaction_survey.questions[int(q_id)-1].question
            choices = satisfaction_survey.questions[int(q_id)-1].choices

            return render_template('question.html', status=status, title=title, question=question, choices=choices)

        else: 
            next_question = len(session[RESPONSE])+1
            flash("You may not proceed or jump questions in the survey without answering the current question")
            return redirect(f"/survey/{next_question}")
    
    else:
        next_question = len(session[RESPONSE])+1
        flash("The given URL does not exist, or is beyond the scope of this survey.")
        return redirect(f"/survey/{next_question}")   

@app.route('/answer', methods=["POST"])
def process_answer():
    """Handle the answer part of the survey and append it to the RESPONSE list"""
    user_input = request.form['answer']

    #Grab the current RESPONSE list that is outside the function's scope, add to it, and update it's original variable with the new list.
    current_list = session[RESPONSE]
    current_list.append(user_input)
    session[RESPONSE] = current_list

    #When this route is triggered, update the redirect_num to assist this POST route in finding the next question.
    new_num = session["redirect"] + 1
    session["redirect"] = new_num

    #Redirect the user to the next question.
    #Logic that checks if the redirect needs to be to the next question, or the /complete route. 
    if len(session[RESPONSE]) == length:
        return redirect('/complete')

    else:
        return redirect(f'/survey/{session["redirect"]}')

@app.route('/complete')
def complete():
    return render_template('complete.html', response=session[RESPONSE])
