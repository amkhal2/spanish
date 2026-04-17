from flask import Flask, render_template, jsonify, request
from excel import get_rows
from flask_sqlalchemy import SQLAlchemy
import os, random
from itertools import cycle  # to go throw category list items continuosly
from unidecode import unidecode # to remove the french accents from string in db

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

##### Development database:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite3")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

dic_file = r"Spanish Dictionary.xlsx"



# Create database table using SQLAlchemy
class Spanish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String, unique=True)
    sound = db.Column(db.String)
    meaning = db.Column(db.String)



## 1) CREATE THE DATABASE: Run Python shell with "python" command --->
##    import db with "from app import db" 
##    ---> creat db with "db.create_all()"

## 2) FILL IN THE DATABASE TABLE:

# rows = get_rows(excel_file) # Parse "Mon Dictionnaire.xlsx" Excel file rows
# errors = ''
# for row in rows:
    # mot = French(word=row[0], cat=row[1], meaning=row[2])
    # db.session.add(mot)

## db.session.commit() --> saving items after they were added to database
# try:
    # db.session.commit()
# except Exception as e:
    # errors = errors + f"<p>{e}<p>" + "<br>"
      
     
# BUILD THE QUIZ - ONE QUESTION & 4 ANSWERS:    
def quiz():
    # select 4 random records from db:
    results = db.engine.execute(''' SELECT * FROM Spanish ORDER BY RANDOM() LIMIT 4''')
    # count the # of records in db:
    rows = db.engine.execute(''' SELECT COUNT(id) FROM Spanish''')
    count = [i[0] for i in rows][0] # will return the no. of rows in db as integer
    
    l = []
    for result in results:
        d = {}
        d["word"] = [result.word, result.id]
        d["sound"] = [result.sound, result.id]
        d["meaning"] = [result.meaning, result.id]
        l.append(d)
    
    def get_choices(some_list, some_key):
    # will get values for some key in a list of dics
        choices = []
        for element in some_list:
            choices.append(element[some_key])
        return choices

    sample = random.choice(l)
    k, v = random.choice(list(sample.items()))
 
    if k == 'word':
       possibility = [(f'What is the English for "<span>{v[0]}</span>"?',sample["meaning"], get_choices(l,"meaning")), 
                        (f'What is the sound of "<span>{v[0]}</span>"?',sample["sound"], get_choices(l,"sound"))]
       question, answer, choix = random.choice(possibility)
    if k == 'sound':
        question, answer, choix = (f'What is the Spanish for this sound "<span>{v[0]}</span>"?',sample["word"], get_choices(l,"word"))
    if k == 'meaning':
        question, answer, choix = (f'What is the Spanish for "<span>{v[0]}</span>"?',sample["word"], get_choices(l,"word"))
        
    return question, answer, choix, count
    


def typing_quiz():
    # select 1 random record from db:
    results = db.engine.execute(''' SELECT * FROM Spanish ORDER BY RANDOM() LIMIT 1''')
    # count the # of records in db:
    rows = db.engine.execute(''' SELECT COUNT(id) FROM Spanish''')
    count = [i[0] for i in rows][0] # will return the no. of rows in db as integer
    
    results = [(i.word, i.id) for i in results]
    question = f"<span class='ruski'>{results[0][0]}</span>"
    questionID = results[0][1]
        
    return question, questionID, count

@app.route('/')
def index():
    # show errors while filling the database (line 29 above)
    # return errors
    
    return render_template('index.html')

@app.route('/manage')
def manage():
    return render_template('manage.html')



@app.route('/typing')
def typing():
    return render_template('typing.html')

@app.route('/get_typing', methods=['POST'])
def get_typing():    
    # get the list of IDs from front end
    data = request.get_json()
    IDs = data['IDs']
      
    # Check that ID is unique
    while True:
        # UNWRAP THE TUPLE --> the 'typing_quiz()'function  
        # returns a tuple of 3 items (question, questionID, count)  
        question, questionID, count = typing_quiz()
        questionID = str(questionID)
        # questionID = '846'
        if len(IDs) == count:
            IDs = []
        if questionID in IDs:
            question, questionID, count = typing_quiz()
            questionID = str(questionID)   
        if questionID not in IDs:
            IDs.append(questionID)
            break

                
    data = {
        "IDs": IDs,
        "question": question,
        "questionID": questionID
        }
    
    return jsonify(data) 
   

@app.route('/get_quiz', methods=['POST'])
def get_quiz():    
    # get the list of IDs from front end
    data = request.get_json()
    IDs = data['IDs']
    
    # Check that ID is unique
    while True:
        # UNWRAP THE TUPLE --> the 'quiz()'function  
        # returns a tuple of 4 items (question, correct answer, choices, count)  
        question, answer, choices, count = quiz()
        questionID = str(answer[-1])
        # questionID = '846'
        if len(IDs) == count:
            IDs = []
        if questionID in IDs:
            question, answer, choices, count = quiz()
            questionID = str(answer[-1])   
        if questionID not in IDs:
            IDs.append(questionID)
            break

                
    data = {
        "IDs": IDs,
        "question": question,
        "questionID": questionID,
        "answers": [
                {'answer_id': choices[0][-1], 'answer': choices[0][0]},
                {'answer_id': choices[1][-1], 'answer': choices[1][0]},
                {'answer_id': choices[2][-1], 'answer': choices[2][0]},
                {'answer_id': choices[3][-1], 'answer': choices[3][0]}
            ]
        }
    
    return jsonify(data)

   
@app.route('/search_Database', methods=['POST'])
def search_Database():
    data = request.get_json()
    
    if data["userInput"].strip() and len(data["userInput"].strip()) > 1: 
        results = Spanish.query.filter(Spanish.word.like(f'%{data["userInput"]}%') | Spanish.meaning.like(f'%{data["userInput"]}%')).all()
               
        l = [[i.id, i.word.replace(unidecode(data["userInput"]),f'<i class="searching">{unidecode(data["userInput"])}</i>'),
        i.sound, i.meaning.replace(unidecode(data["userInput"]),f'<i class="searching">{unidecode(data["userInput"])}</i>')] for i in results]
        if l:
            return jsonify({"res": l, 'status':'success'})
        
    return jsonify({"res": 'No results found!'})


@app.route('/find_word', methods=['POST'])
def find_word():
    data = request.get_json()
    
    result = French.query.filter_by(word=data["clickedWord"]).first()
    if result:
        return jsonify({"response": "success","id": result.id, "word": result.word, "cat": result.cat, "meaning": result.meaning})
    else:
        return jsonify({"response": "No results found!" })

@app.route("/add_record", methods=['POST'])
def add_record():
    # when the user clicks the "add" button
    data = request.get_json()
    entry = French(word=data['word'], cat=data['cat'], meaning=data['meaning'])
    db.session.add(entry)
    
    try:
        db.session.commit()
        db.session.refresh(entry)
        return jsonify({ 'res': 'Record successfully added to database :-)',
                        'id': entry.id
        })
        
    except Exception as e:
        return jsonify({ 'res': f'Error while writing record to db: {e}' })  

@app.route("/find_record", methods=['POST'])
def find_record():
    # when user clicks the find button
    data = request.get_json()
    db_id = int(data["id"])
    try:
        result = French.query.filter_by(id=db_id).first()    
        to_client = [result.word, result.cat, result.meaning, result.id] 
    except Exception as e:
        to_client = [str(e)]

        
    return jsonify({'res': to_client})

@app.route('/update_record', methods = ['POST'])
def update_record():
    # when clicking "update" button
    data = request.get_json()
    id = data['id']
    word = data['word']
    cat = data['cat']
    meaning = data['meaning']
    word_u = unidecode(word)
    meaning_u = unidecode(meaning)
    try:
        db.engine.execute('update French set word = ?, cat = ?, meaning = ?, word_unaccented=?, meaning_unaccented=?  where id = ?',
                            (word, cat, meaning, word_u, meaning_u , id))
        return jsonify({
        'res': 'Record updated Successfully!', 'class': 'success'
         })
    except Exception as e:
        return jsonify({
        'res': str(e)[:49], 'class': 'fail'
         })

   
if __name__ == "__main__":
    app.run(debug=True)