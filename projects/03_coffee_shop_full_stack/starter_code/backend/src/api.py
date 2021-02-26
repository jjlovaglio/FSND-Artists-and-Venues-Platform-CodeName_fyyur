import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint - done
        it should contain only the drink.short() data representation - done
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks - done
        or appropriate status code indicating reason for failure - done
'''
@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    drinks = list(map(Drink.short, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table - done
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation - done
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink - done
        or appropriate status code indicating reason for failure - done
'''
@app.route("/drinks", methods=['POST',])
# @requires_auth('post:drinks')
def post_drinks():
    # get title and recipe from request
    title = request.args.get("title")
    recipe = request.args.get("recipe")


    if title is None or recipe is None:
        abort(400)

    # check that drink is not already in the database
    drink = Drink.query.filter_by(title=title).one_or_none()
    if drink is None or drink.title != title :
        # create & insert object to db
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        
        # retrieve newly created drink from database
        drink = Drink.query.filter_by(title=title).one_or_none()

    else:    
        # abort and msg in terminal
        print('Drink already exists in the database.')
        abort(400)

    formatted_drink = [drink.long()]


    result = {
        "success": True,
        "drinks": formatted_drink
    }
    return jsonify(result)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
