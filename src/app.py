#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def main():
    """Main page with a form to submit user input."""
    return '''
     <form action="/echo_user_input" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    """Echoes the user input back to the user."""
    input_text = request.form.get("user_input", "")
    return "You entered: " + input_text
