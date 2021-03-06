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
    # query db for all drinks
    drinks = Drink.query.all()
    # if no records on db, abort 404 returning json,
    # using custom error handler
    if len(drinks) == 0:
        abort(404)
    # format list of drink objects with drink.short() method
    drinks = list(map(Drink.short, Drink.query.all()))

    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission - done
        it should contain the drink.long() data representation - done
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks - done
        or appropriate status code indicating reason for failure - done
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    # query db for all drinks
    drinks = Drink.query.order_by(Drink.id).all()
    # if no records on db, abort 404 returning json,
    # using custom error handler
    if len(drinks) == 0:
        abort(404)

    # format drink for json using long method
    formatted_drinks = [drink.long() for drink in drinks]

    result = {
        "success": True,
        "drinks": formatted_drinks
    }
    return jsonify(result)


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
@requires_auth('post:drinks')
def post_drink(payload):
    # get title and recipe from request
    title = request.args.get("title")
    recipe = request.args.get("recipe")

    body = request.get_json()
    if body:
        title = body['title']
        recipe = json.dumps([body['recipe']])

    if title is None or recipe is None:
        abort(422)

    # check that drink is not already in the database
    drink = Drink.query.filter_by(title=title).one_or_none()
    if drink is None or drink.title != title :
        try:
            # create & insert object to db
            drink = Drink(title=title, recipe=recipe)
            drink.insert()
            
            # retrieve newly created drink from database
            drink = Drink.query.filter_by(title=title).one_or_none()
        except:   
            abort(422)

    # format drink object as array for json sending
    formatted_drink = [drink.long()]


    result = {
        "success": True,
        "drinks": formatted_drink
    }
    return jsonify(result)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id - ok
        it should respond with a 404 error if <id> is not  found - done
        it should update the corresponding row for <id> - done
        it should require the 'patch:drinks' permission - done
        it should contain the drink.long() data representation - done
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink - done
        or appropriate status code indicating reason for failure - done
'''
@app.route("/drinks/<int:drink_id>", methods=['PATCH',])
@requires_auth('patch:drinks')
def patch_drink(payload, drink_id):
    # query drink by id
    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(401)

    # get updates from request
    title = request.args.get("title")
    recipe = request.args.get("recipe")

    if title is None or recipe is None:
        abort(422)

    # modify the drink object
    drink.title = title
    drink.recipe = recipe
    # update to db
    drink.update()

    formatted_drink = [drink.long()]

    result = {
        "success": True,
        "drinks": formatted_drink
    }
    return jsonify(result)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id - ok
        it should respond with a 404 error if <id> is not found - ok
        it should delete the corresponding row for <id> - ok
        it should require the 'delete:drinks' permission - ok
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record -ok
        or appropriate status code indicating reason for failure - ok
'''

@app.route("/drinks/<int:drink_id>", methods=['DELETE',])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(401)
    
    deleted_id = drink.id
    try:
        drink.delete()
        print(f'drink: {drink.id} {drink.title} was deleted from db.')
    except Exception:
        abort(422)

    result = {
        "success": True,
        "delete": deleted_id
    }

    return jsonify(result)



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
    error handler should conform to general task above - done
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(err):
    return jsonify({
                    "success": False,
                    "error": err.status_code,
                    "message": err.error['code']
                    }), err.status_code