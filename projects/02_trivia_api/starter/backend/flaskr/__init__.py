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
      'current_category':None,
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

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
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

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    