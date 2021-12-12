import logging, traceback, os, requests

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# home route
@app.route("/")
def hello():
    return render_template('index.html', name='Jane', gender='Female')


# serving form web page
@app.route("/my-form")
def form():
    return render_template('form.html')


# handling form data
@app.route('/form-handler', methods=['POST'])
def handle_data():
    return jsonify(request.form)


@app.route("/characters")
def characters():
    pics = ["character_back.jpg"]

    response = requests.get('http://localhost:8080/cards/characters')

    if response.status_code == 200:
        characters = response.json()

        print(characters)

        pics = list(map(lambda x: x["name"].lower() + ".jpg", characters))

        print(pics)

    return render_template("characters.html", pics=pics)


if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=8081)

    except Exception:
        logging.error(traceback.format_exc())
