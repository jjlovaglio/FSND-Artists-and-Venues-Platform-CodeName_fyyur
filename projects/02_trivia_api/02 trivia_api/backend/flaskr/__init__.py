import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs - done
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow - done
  '''

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories. - done
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id:category.type for category in categories}

    return jsonify({

      'success': True,
      'categories': formatted_categories,
      'total_categories': len(Category.query.all())

    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). - done
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. - done

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. - done
  '''
  SELECTION_PER_PAGE = 10
  def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * SELECTION_PER_PAGE
    end = start + SELECTION_PER_PAGE
    selection = [item.format() for item in selection]
    current_selection = selection[start:end]

    return current_selection

  @app.route('/questions', methods=['GET'])
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate(request, selection)

    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id:category.type for category in categories}


    return jsonify({
      'success': True,
      'questions': current_questions,
      'categories': formatted_categories,
      'current_category': None,
      'total_questions': len(Question.query.all()),

    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. - done

  TEST: When you click the trash icon next to a question, the question will be removed. - done
  This removal will persist in the database and when you refresh the page. - done
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

    question = Question.query.filter(Question.id == question_id).one_or_none()

    if question is None:
      abort(404)
      
    current_category = question.category
    question.delete()
    print(f'question: {question.id} {question.question} was deleted from db.')
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate(request, selection)
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id:category.type for category in categories}
    return jsonify({
      'success':True,
      'questions':current_questions,
      'categories': formatted_categories,
      'total_questions': len(Question.query.all()),
      'current_category':current_category,
    })



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score. - done

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  - done
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    if body is None:
      abort(400)
    
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
    question.insert()
    print(f'question: {question.id} {question.question} was created!')

    return jsonify({
        'success':True,

      })


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. - done

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. - done
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    data = request.get_json()
    search_term = data.get('searchTerm')

    if not search_term:
      abort(422)
    
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    if not questions:
      abort(422)
    
    paginated_questions = paginate(request, questions)

    return jsonify({
      'success': True,
      'questions': paginated_questions,

    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. - done

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. - done
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['POST'])
  def get_questions_by_category(category_id):
    # get categories from db
    category = Category.query.get(category_id)
    # filter questions by category
    questions = Question.query.filter(Question.category == category_id).all()
    # convert questions to json friendly format


    return jsonify({
      'success': True,
      'questions': paginate(request, questions),
      'total_questions': len(questions),
      'current_category': category.type
    })



  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    # get questions to play the quiz
    body = request.get_json()
    # take previous_question parameter
    previous_questions = body.get('previous_questions', [])
    # take category parameter
    quiz_category = body.get('quiz_category', None)
    # return a random question within the given category if provided and
    # that is not one of the previous questions.

    # get category_id from frontend
    category_id = int(quiz_category["id"])
    # if there is a quiz category and if the id is 0,
    # query all questions
    # else, filter questions by category id.
    if quiz_category:
      if quiz_category["id"] == 0:
        quiz = Question.query.all()
      else:
        quiz = Question.query.filter_by(category=category_id).all()
    # if there are no questions for the selected category, abort 422.
    if not quiz:
      return abort(422)
    selected = []
    # for every question in the quiz, if its id is not in the previous_questions list,
    # append question to selected list formatted as a dict.
    for question in quiz:
      if question.id not in previous_questions:
        selected.append(question.format())
    # if selected contains questions
    if len(selected) != 0:
      # select a random question and
      result = random.choice(selected)
      # return to frontend as a JSON object
      return jsonify({
        'question': result
      })
    # else, return question key as false.
    else:
      return jsonify({
        'question': False
      })





  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. - done
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "Bad Request: The request cannot be fulfilled due to bad syntax"
    }), 400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Not Found: The request resource could not be found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': "Method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable Entity: The request was well formed but was unable to be followed due to semantic errors"
    }), 422

  return app

    