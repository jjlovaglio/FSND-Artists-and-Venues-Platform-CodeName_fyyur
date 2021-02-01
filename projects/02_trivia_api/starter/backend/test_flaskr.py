import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Test Create New Question',
            'answer': 'Answer Create New Question',
            'category': 2,
            'difficulty': 2
        }

        self.new_question_2 = Question(
                            question='test question',
                             answer='test answer',
                             category=2,
                            difficulty=2)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    

    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_categories(self):
        """ Tests getting categories """

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])


    def test_get_questions(self):
        """ Tests getting questions """

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertIsNone(data['current_category'])


    def test_404_when_getting_nonexistent_page(self):
        """ Tests 404 not found on page 1.000"""

        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found: The request resource could not be found")


    def test_delete_question(self):
        """ Tests deleting a question of id:24 """

        # dummy question created for testing endpoint
        # question inserted in the db
        self.new_question_2.insert()
        # question retrieved from db
        question = Question.query.filter(Question.question == 'test question').one_or_none()
        # question deleted 
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'], question.category)


    def test_404_when_question_to_be_deleted_not_found(self):
        """ Tests 404 error being raised when q's to be deleted is not found e.g. id 1"""

        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not Found: The request resource could not be found")


    def test_create_question(self):
        """" tests creating questions """

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # delete question from the database
        question = Question.query.filter(Question.question == 'Test Create New Question').one_or_none()
        question.delete()


    def test_400_no_json_received_to_create_question(self):
        """" tests error 400 when no json is received in create question endpoint """

        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Bad Request: The request cannot be fulfilled due to bad syntax")


    def test_search_questions(self):
        """ Tests the post request for searching questions """

        res = self.client().post('/questions/search', json={'searchTerm': 'Peanut'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])


    def test_422_search_term_nonexistent_in_json_response(self):
        """" Tests case when searchTerm key doesn't provide any value in the response json """

        res = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Unprocessable Entity: The request was well formed but was unable to be followed due to semantic errors")


    def test_422_search_term_not_found_in_db(self):

        res = self.client().post('/questions/search', json={'searchTerm': 'Serendipity'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Unprocessable Entity: The request was well formed but was unable to be followed due to semantic errors")


    def test_post_questions_by_category(self):

        res = self.client().post('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Art')


    def test_quiz(self):

        res = self.client().post('/quizzes', json={'previous_question':[], 
                                                       'quiz_category': {'id': 1},
                                                        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
   
   
    def test_error_422_quiz_category_out_of_range(self):
        """ Test submitting an id that exceeds the existing range of category id's """

        res = self.client().post('/quizzes', json={'previous_question':[], 
                                                       'quiz_category': {'id': 23},
                                                        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], "Unprocessable Entity: The request was well formed but was unable to be followed due to semantic errors")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()