import subprocess
# This is a sample Python/Flask app showing Domino's App publishing functionality.
# You can publish an app by clicking on "Publish" and selecting "App" in your
# quick-start project.
import json
import flask
from flask import request, redirect, url_for, jsonify
import numpy as np
import os

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        script_name = os.environ.get('DOMINO_RUN_HOST_PATH', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        # Setting wsgi.url_scheme from Headers set by proxy before app
        scheme = environ.get('HTTP_X_SCHEME', 'https')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

# Homepage - show help page with all available endpoints
@app.route('/')
def index_page():
    return help_page()

# Sample redirect using url_for
@app.route('/redirect_test')
def redirect_test():
    return redirect(url_for('another_page'))

# Sample return string instead of using template file
@app.route('/another_page')
def another_page():
    msg = "You made it with redirect( url_for('another_page') )." + \
          "A call to flask's url_for('index_page') returns " + url_for('index_page') + "."
    return msg

# Original random endpoint with optional path parameter
@app.route("/random")
@app.route("/random/<int:n>")
def random(n=100):
    random_numbers = list(np.random.random(n))
    return json.dumps(random_numbers)

# NEW: Query parameter examples

# Example 1: Basic query parameters
@app.route("/greet")
def greet():
    """
    Access with query parameters:
    /greet?name=John&age=25
    /greet?name=Jane
    /greet
    """
    name = request.args.get('name', 'World')
    age = request.args.get('age', type=int)
    
    greeting = f"Hello, {name}!"
    if age:
        greeting += f" You are {age} years old."
    
    return jsonify({
        "message": greeting,
        "query_params": dict(request.args)
    })

# Example 2: Multiple query parameters with defaults
@app.route("/calculate")
def calculate():
    """
    Access with query parameters:
    /calculate?operation=add&x=10&y=5
    /calculate?operation=multiply&x=3&y=7
    /calculate?x=15&y=3  (defaults to 'add')
    """
    operation = request.args.get('operation', 'add')
    x = request.args.get('x', default=0, type=float)
    y = request.args.get('y', default=0, type=float)
    
    result = None
    if operation == 'add':
        result = x + y
    elif operation == 'subtract':
        result = x - y
    elif operation == 'multiply':
        result = x * y
    elif operation == 'divide':
        result = x / y if y != 0 else 'Error: Division by zero'
    else:
        result = 'Error: Invalid operation'
    
    return jsonify({
        "operation": operation,
        "x": x,
        "y": y,
        "result": result,
        "query_params": dict(request.args)
    })

# Example 3: List/array parameters
@app.route("/stats")
def stats():
    """
    Access with query parameters:
    /stats?numbers=1,2,3,4,5
    /stats?numbers=10,20,30&operation=mean
    /stats?numbers=1,2,3,4,5&operation=sum
    """
    numbers_str = request.args.get('numbers', '1,2,3,4,5')
    operation = request.args.get('operation', 'all')
    
    try:
        numbers = [float(x.strip()) for x in numbers_str.split(',')]
    except ValueError:
        return jsonify({"error": "Invalid numbers format. Use comma-separated values."})
    
    result = {}
    if operation == 'all' or operation == 'mean':
        result['mean'] = np.mean(numbers)
    if operation == 'all' or operation == 'sum':
        result['sum'] = np.sum(numbers)
    if operation == 'all' or operation == 'std':
        result['std'] = np.std(numbers)
    if operation == 'all' or operation == 'min':
        result['min'] = np.min(numbers)
    if operation == 'all' or operation == 'max':
        result['max'] = np.max(numbers)
    
    return jsonify({
        "numbers": numbers,
        "operation": operation,
        "results": result,
        "query_params": dict(request.args)
    })

# Example 4: Boolean parameters
@app.route("/data")
def data():
    """
    Access with query parameters:
    /data?format=json&include_metadata=true
    /data?format=csv&sort=desc
    /data?limit=10&include_metadata=false
    """
    format_type = request.args.get('format', 'json')
    limit = request.args.get('limit', default=5, type=int)
    sort_order = request.args.get('sort', 'asc')
    include_metadata = request.args.get('include_metadata', 'false').lower() == 'true'
    
    # Sample data
    sample_data = [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 85},
        {"id": 3, "name": "Charlie", "value": 92},
        {"id": 4, "name": "Diana", "value": 78},
        {"id": 5, "name": "Eve", "value": 95},
        {"id": 6, "name": "Frank", "value": 88},
        {"id": 7, "name": "Grace", "value": 91}
    ]
    
    # Apply sorting
    if sort_order == 'desc':
        sample_data.sort(key=lambda x: x['value'], reverse=True)
    else:
        sample_data.sort(key=lambda x: x['value'])
    
    # Apply limit
    limited_data = sample_data[:limit]
    
    response_data = {
        "data": limited_data,
        "query_params": dict(request.args)
    }
    
    if include_metadata:
        response_data["metadata"] = {
            "total_records": len(sample_data),
            "returned_records": len(limited_data),
            "format": format_type,
            "sort_order": sort_order
        }
    
    if format_type == 'csv':
        # Simple CSV format
        csv_lines = ["id,name,value"]
        for item in limited_data:
            csv_lines.append(f"{item['id']},{item['name']},{item['value']}")
        return "\n".join(csv_lines), 200, {'Content-Type': 'text/csv'}
    
    return jsonify(response_data)

# Example 5: Enhanced random endpoint with query parameters
@app.route("/random_enhanced")
def random_enhanced():
    """
    Access with query parameters:
    /random_enhanced?count=10&min=0&max=100&seed=42
    /random_enhanced?count=5&distribution=normal
    /random_enhanced?count=20&min=1&max=6&format=integers
    """
    count = request.args.get('count', default=10, type=int)
    min_val = request.args.get('min', default=0, type=float)
    max_val = request.args.get('max', default=1, type=float)
    seed = request.args.get('seed', type=int)
    distribution = request.args.get('distribution', 'uniform')
    format_type = request.args.get('format', 'float')
    
    if seed:
        np.random.seed(seed)
    
    if distribution == 'normal':
        numbers = np.random.normal(0, 1, count)
    else:  # uniform
        numbers = np.random.uniform(min_val, max_val, count)
    
    if format_type == 'integers':
        numbers = [int(x) for x in numbers]
    else:
        numbers = [float(x) for x in numbers]
    
    return jsonify({
        "numbers": numbers,
        "parameters": {
            "count": count,
            "min": min_val,
            "max": max_val,
            "seed": seed,
            "distribution": distribution,
            "format": format_type
        },
        "query_params": dict(request.args)
    })

# Help endpoint to show all available endpoints
@app.route("/help")
def help_page():
    """Show all available endpoints with example URLs"""
    base_url = request.host_url.rstrip('/')
    
    endpoints = [
        {
            "endpoint": "/greet",
            "description": "Greet with optional name and age",
            "examples": [
                f"{base_url}/greet?name=John&age=25",
                f"{base_url}/greet?name=Jane",
                f"{base_url}/greet"
            ]
        },
        {
            "endpoint": "/calculate",
            "description": "Perform calculations with query parameters",
            "examples": [
                f"{base_url}/calculate?operation=add&x=10&y=5",
                f"{base_url}/calculate?operation=multiply&x=3&y=7",
                f"{base_url}/calculate?x=15&y=3"
            ]
        },
        {
            "endpoint": "/stats",
            "description": "Calculate statistics on comma-separated numbers",
            "examples": [
                f"{base_url}/stats?numbers=1,2,3,4,5",
                f"{base_url}/stats?numbers=10,20,30&operation=mean",
                f"{base_url}/stats?numbers=1,2,3,4,5&operation=sum"
            ]
        },
        {
            "endpoint": "/data",
            "description": "Get sample data with formatting options",
            "examples": [
                f"{base_url}/data?format=json&include_metadata=true",
                f"{base_url}/data?format=csv&sort=desc",
                f"{base_url}/data?limit=10&include_metadata=false"
            ]
        },
        {
            "endpoint": "/random_enhanced",
            "description": "Generate random numbers with various options",
            "examples": [
                f"{base_url}/random_enhanced?count=10&min=0&max=100&seed=42",
                f"{base_url}/random_enhanced?count=5&distribution=normal",
                f"{base_url}/random_enhanced?count=20&min=1&max=6&format=integers"
            ]
        }
    ]
    
    return jsonify({
        "message": "Available endpoints with query parameter examples",
        "endpoints": endpoints
    })

@app.after_request
def add_cors_to_static(response):
    # if the request was for anything under /static/, add CORS
    if flask.request.path.startswith('/static/'):
        response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)