from flask import Flask, render_template, request, session, redirect, flash, url_for, send_file
from flask_mail import Mail, Message
from model.feedback_model import Feedback
from model.question_modules import Questions
from model.redacteur_module import Redacteur, AddRedacteur
from model.users import User
from model.prompt_modules import PromptModules
from lib.gpt.bloom_taxonomy import get_bloom_category
import json
import sqlite3
import os
from settings.settings import database
from model.active_redacteur_module import ActiveRedacteur

DATABASE_PATH = './databases/database.db'

app = Flask(__name__)

app.secret_key = 'hello'

email_user= os.getenv("EMAIL_USERNAME")
email_pass= os.getenv("EMAIL_PASSWORD")

app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT =587,
    MAIL_USE_SSL = False,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = email_user,
    MAIL_PASSWORD = email_pass,
)

app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/redacteur')
def redacteuren_beheer():
    if not session.get('user') or not session['user'].get('is_admin'):
        flash("Alleen toegankelijk voor admins.")
        return redirect(url_for('homepage'))

    redacteur_model = Redacteur(database)
    redacteurs = redacteur_model.get_all_redacteurs()
    return render_template('redacteur_pages/redacteur.html.jinja', redacteurs=redacteurs)


@app.route('/update_redacteur_admin', methods=['POST'])
def update_redacteur_admin():
    redacteur_model = Redacteur(database)

    if 'delete_redacteur' in request.form:
        login_to_delete = request.form['delete_redacteur']
        redacteur_model.delete_redacteur(login_to_delete)
        # redacteur_model.null_redacteur(login_to_delete)
        return redirect(url_for('redacteuren_beheer'))

    for redacteur in redacteur_model.get_all_redacteurs():
        login = redacteur['login']
        is_admin = request.form.get(f'is_admin_{login}')
        is_admin = 1 if is_admin else 0
        redacteur_model.update_admin_status(login, is_admin)

    return redirect(url_for('redacteuren_beheer'))


# adjust_redactor
@app.route('/adjust_redactor')
def adjust_redactor():
    if 'login' not in session:
        return redirect(url_for('login_page'))

    login = session['login']
    active_redacteur = ActiveRedacteur(database)
    redacteur_info = active_redacteur.get_active_redacteur(login)
    return render_template('redacteur_pages/adjust_redactor.html.jinja', user=redacteur_info)


@app.route('/update_redacteur', methods=['POST'])
def update_redacteur():
    login = session['login']
    display_name = request.form['naam']
    email = request.form['email']
    password = request.form['wachtwoord']
    is_admin = request.form.get('is_admin', 'off') == 'on'

    active_redacteur = ActiveRedacteur(database)
    active_redacteur.update_redacteur(login, display_name, email, password, is_admin)

    flash("Uw gegevens zijn succesvol bijgewerkt")


    return redirect(url_for('adjust_redactor'))


#redacteur
@app.route('/redacteur')
def redacteur():
    if session.get('login'):
        return render_template('redacteur_pages/redacteur.html.jinja')
    else:
        return redirect(url_for('login_page'))

#about us
@app.route('/aboutus')
def about_us():
    return render_template('about_us.html.jinja')


#feedback
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        feedback_title = request.form['feedback-title-input']
        feedback_text = request.form['feedback-input']
        feedback_model = Feedback(database)
        save_feedback = feedback_model.save_feedback(feedback_title, feedback_text)
        print(feedback_title, feedback_text)
        flash('Feedback saved.')
    if session.get('login'):
        return render_template('feedback-page.html.jinja')
    else:
        return redirect(url_for('login_page'))

#home
@app.route('/home')
def homepage():
    if session.get('login'):
        return render_template('homepage.html.jinja')
    else:
        return redirect(url_for('login_page'))

#add-redacteur
@app.route('/add_redacteur')
def add_redacteur():
    if session.get('login'):
        return render_template('redacteur_pages/add_redacteur.html.jinja')
    else:
        return redirect(url_for('login_page'))


@app.route('/add_redacteur/submit', methods=['POST'])
def submit_redacteur():
    display_name = request.form.get('naam')
    login = request.form.get('email')
    password = request.form.get('wachtwoord')
    is_admin = 1 if request.form.get('is_admin') else 0
    add_redacteur = AddRedacteur(database)
    add_redacteur.new_redacteur(display_name, login, password, is_admin)
    return redirect(url_for('redacteur'))


#index taxonomy
@app.route('/taxonomy/index/<questions_id>/<prompt_type>')
def taxonomy(questions_id, prompt_type):
    question_model = Questions(database)
    single_question = question_model.show_single_question(questions_id)
    print(single_question)
    request_prompts = PromptModules(database)

    prompts = request_prompts.show_prompt_type(prompt_type)

    return render_template('index_pages/indexing-taxonomy.html.jinja',
                           prompts=prompts,
                           single_question=single_question,
                           prompt_type=prompt_type)


@app.route('/taxonomy/check/<questions_id>/<prompt_type>', methods=['POST', 'GET'])
def taxonomy_check(questions_id, prompt_type):
    questions_model = Questions(database)
    single_question = questions_model.show_single_question(questions_id)

    form_prompt_id = request.form.get('prompts')
    form_prompt = PromptModules(database).show_prompt(form_prompt_id)
    bloom_category = None

    try:
        bloom_category = get_bloom_category(single_question['question'], form_prompt["prompt"], 'dry_run')
        print("----bloom: ", bloom_category)

        if not bloom_category:
            flash(f"Er ging iets mis met het ophalen de GTP-analyse. Probeer het opnieuw.")
            return redirect(url_for('taxonomy', questions_id=questions_id, prompt_type=prompt_type))
        else:
            flash(f"GPT Resultaat: {bloom_category['niveau']} - {bloom_category['uitleg']}")

    except Exception as e:
        flash(f"Er is een fout opgetreden bij het ophalen van GPT-data: {str(e)}")

    # if request.method == 'POST':
    #     taxonomy_input = request.form.get('taxonomy')
    #     taxonomy = questions_model.update_taxonomy(taxonomy_input, questions_id, prompt_type)
    #     prompt = request.form.get('prompt')


    return render_template('index_pages/control-question-page.html.jinja',
                           questions_id=questions_id,
                           single_question=single_question,
                           bloom_category=bloom_category,
                           form_prompt_id=form_prompt_id,
                           prompt_type=prompt_type )



@app.route('/taxonomy/save/<questions_id>/<prompt_type>', methods=['POST'])
def save_taxonomy(questions_id, prompt_type):
    question_model = Questions(database)

    taxonomy_bloom = request.form.get('taxonomy')   # categorie volgens de gebruiker
    gpt_taxonomy_bloom = request.form.get('gpt_taxonomy', "") # categorie volgens GPT
    gpt_successful = taxonomy_bloom.lower() == gpt_taxonomy_bloom.lower()
    if gpt_successful:
        flash("GPT beoordeling van de taxonomie overgenomen.")
    else:
        flash("Eigen beoordeling opgeslagen.")

    form_prompt_id = request.form.get('form_prompt_id', "")
    PromptModules(database).update_prompt_success_count(form_prompt_id, success=gpt_successful)

    user_id = session.get('user')['user_id']

    is_updated = question_model.update_taxonomy(taxonomy_bloom, questions_id, prompt_type, user_id)
    if is_updated:
        print(taxonomy_bloom)
        return redirect("/questions")
    else:
        flash("Er ging iets mis bij het opslaan van de taxonomie.")
        return redirect(f"/taxonomy/check/{questions_id}/{prompt_type}")

#login
@app.route('/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login = request.form.get('login-input')
        password = request.form.get('password-input')
        user_model = User()
        user = user_model.show_user(login, password)

        if user is None:
            session.pop('login', None)
            flash('Login failed!')
            return redirect(url_for('login_page'))
        else:
            session['login'] = login
            session['user'] = {
                'user_id': user['user_id'],
                'is_admin': user['is_admin'],
            }
            return redirect(url_for('homepage'))
    return render_template('login-page.html.jinja')


#questions
@app.route("/questions")
def question_page():
    # Geeft page 0 aan als default en limiteert vragen tot maximaal 20
    page = int(request.args.get('page', 0))
    offset = page * 20

    # This code requests the values bellow if they are given or selected
    question = request.args.get('searching')
    school_year = request.args.get('school_year')
    education_level = request.args.get('education_level')
    subject = request.args.get('subject')

    # This piece of code gives the requested values above to the module.
    # Inside the module the query is modified with a AND, WHERE and a LIKE statement if needed.
    question_model = Questions(database)
    questions = question_model.show_questions(
        question_search = question,
        school_year = school_year,
        education_level = education_level,
        subject = subject,
        offset =  offset,
    )


    if session.get('login'):
        return render_template('question_pages/questions.html.jinja', questions=questions, page=page)
    else:
        return redirect(url_for('login_page'))



@app.route('/import', methods=['GET', 'POST'])
def import_page():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.json'):
            data = json.load(file)
            question_model = Questions(database)
            question_model.import_questions(data)
            flash("Questions imported succesfully")
            return redirect(url_for('import_page'))
    return render_template('question_pages/import.html.jinja')


#function to connect to database
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


#route to export page
@app.route('/export')
def index():
    conn = get_db_connection()
    questions = conn.execute('SELECT questions_id, question FROM questions').fetchall()
    conn.close()
    return render_template('question_pages/export.html.jinja', questions=questions)


#export/download json file
@app.route('/export', methods=['GET', 'POST'])
def export_question():
    if request.method == 'POST':
        question_id = request.form.get('question_id')
        conn = get_db_connection()
        question_data = conn.execute('SELECT * FROM questions WHERE questions_id = ?', (question_id,)).fetchone()
        conn.close()

        question_dict = dict(question_data)
        with open('exported_question.json', 'w') as json_file:
            json.dump(question_dict, json_file, indent=4)

        return send_file('exported_question.json', as_attachment=True)


@app.route('/questions/imports')
def import_questions():
    questions = Questions(database)
    questions.import_questions(questions)
    flash("Questions imported successfully")
    return redirect(url_for('homepage'))

    question_model = Questions(database)
    questions = question_model.show_questions()
    if session.get('login'):
        return render_template('question_pages/questions.html.jinja', questions=questions)
    else:
        return redirect(url_for('login_page'))


@app.route("/reviewed_questions")
def reviewed_questions():
    if session.get('login'):
        return render_template('question_pages/reviewed_questions.html.jinja')
    else:
        return redirect(url_for('login_page'))


# This route is used to fill out the necessary information to create a new prompt
# the user id of the user is also given to the module to link the prompt to the person who made it
@app.route('/prompts/add')
def add_prompt():
    if session.get('login'):
        user_id = request.form.get('user_id', "")
        return render_template('prompt_pages/add_prompt.html.jinja', user_id=user_id )
    else:
        return redirect(url_for('login_page'))


# This route is used to request the information the user wrote in the input fields
# and then saves it in the database using a prompt module
@app.route('/prompts/submit', methods=['POST'])
def save_form():
    user_id = session.get('user').get('user_id')
    prompt_name = request.form['prompt_name']
    prompt = request.form['prompt_text']
    prompt_type = request.form['prompt_type']
    save_prompts = PromptModules(database)
    prompt_id = save_prompts.save_new_prompt(user_id, prompt_name, prompt, prompt_type)
    return redirect(url_for("show_prompts"))


@app.route("/prompts/details/confirm/delete/<int:prompts_id>")
def confirm_delete_prompt(prompts_id):
    if not session.get('login'):
        return redirect(url_for('login_page'))
    show_prompt_remove = PromptModules(database)
    prompt = show_prompt_remove.show_prompt(prompts_id)

    if not prompt:
        flash("prompt not found")
        return redirect(url_for('show_prompts'))

    return render_template("prompt_pages/confirm_delete_prompt.html.jinja", prompts_id=prompts_id, prompt=prompt)



@app.route("/prompts/details/delete/<int:prompts_id>", methods=['POST'])
def delete_prompt(prompts_id):
    if session.get('login'):
        try:
            deleting_prompts = PromptModules(database)
            delete_succes = deleting_prompts.remove_prompt(prompts_id)

            if delete_succes:
                flash("Prompt deleted successfully")
            else:
                flash("Prompt could not be deleted")
        except Exception as e:
            flash(f"er is een fout opgetreden tijdens het verwijderen van de prompt: {e}")

        return redirect(url_for('show_prompts'))
    else:
        return redirect(url_for('login_page'))



# This route is used to show details of a prompt to the user based on the prompt they chose to look at
@app.route("/prompts/details/<int:prompts_id>")
def prompt_details(prompts_id):
    single_prompt = PromptModules(database)
    prompt_data = single_prompt.show_prompt(prompts_id)

    if not prompt_data:
        return "Prompt not found", 404

    if session.get('login'):
        return render_template('prompt_pages/prompt_details.html.jinja', prompts_id=prompts_id, prompt=prompt_data)
    else:
        return redirect(url_for('login_page'))


# This route is used to request the data of a prompt after viewing the prompt details of said prompt
# after you hit the edit prompt button the data such as prompt name and the prompt itself are inserted in to the input fields.
# other than that this page works exactly like the prompts/add route
@app.route('/prompts/update/<int:prompts_id>', methods=['GET'])
def update_prompt(prompts_id):
    single_prompt = PromptModules(database)
    prompt_data = single_prompt.show_prompt(prompts_id)

    if session.get('login'):
        return render_template('prompt_pages/update_prompt.html.jinja', prompts_id=prompts_id, prompt=prompt_data)
    else:
        return redirect(url_for('login_page'))


# this route is used to save a updated version of a prompt as a new prompt.
# this app route works the same way the as the prompts/submit route works
@app.route('/prompts/update/submit', methods=['POST'])
def save_updated_prompt():
    user_id = session.get('user').get('user_id')
    prompt_name = request.form['prompt_name']
    prompt = request.form['prompt_text']
    prompt_type = request.form['prompt_type']
    save_prompts = PromptModules(database)
    save_prompts.save_new_prompt(user_id, prompt_name, prompt, prompt_type)

    if session.get('login'):
        return redirect(url_for("show_prompts"))
    else:
        return redirect(url_for('login_page'))







# This route is used to display the prompts in the database
# it also returns any filters selected by a user to the module
# this makes it so the module will return a new list sorted by the filter the user has selected
@app.route('/prompts', methods=['GET'])
def show_prompts():
    if session.get('login'):
        # filters from the website to request prompts in a certain way
        filter_by_alphabetical_order = request.args.get('FilterByAlphabeticalOrder') is not None
        filter_by_succes_rating = request.args.get('FilterBySuccesRating') is not None
        filter_by_questions_count = request.args.get('FilterByQuestionsCount') is not None
        filter_by_prompt_type = request.args.get('FilterByPromptType') is not None

        multiple_prompts = PromptModules(database)
        prompts_list = multiple_prompts.show_multiple_prompts(
            filter_by_alphabetical_order=filter_by_alphabetical_order,
            filter_by_succes_rating=filter_by_succes_rating,
            filter_by_questions_count=filter_by_questions_count,
            filter_by_prompt_type=filter_by_prompt_type
        )

        return render_template('prompt_pages/display_prompts.jinja', prompts=prompts_list)
    else:
        return redirect(url_for('login_page'))


@app.route('/contact_page', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        message = request.form.get('message')
        if len(email) < 4:
            flash('Email must be at least 4 characters')
        elif len(name) < 2:
            flash('Name must be at least 2 characters')
        elif len(message) < 10:
            flash('Message must be at least 10 characters')
        else:
            try:
                msg = Message(
                    subject=f"Message from {name} {email}",
                    sender=email_user,
                    recipients=[email_user],
                    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
                )
                Mail.send(msg)
                flash("Message sent successfully!", 'success')
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "error")

    return render_template("contact_page.html.jinja")

@app.route('/questions/import')
def import_question():
    questions = Questions(database)
    questions.import_questions(questions)
    flash("Questions imported successfully")
    return redirect(url_for('homepage'))



@app.route('/<user_id>/indexed-questions')
def user_indexed_questions(user_id):
    user_model = User()
    username = user_model.show_username(user_id)['display_name']

    question_model = Questions(database)
    questions = question_model.show_user_questions(user_id)
    return render_template('user-questions-indexed.html', username=username, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
