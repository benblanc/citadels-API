# Citadels API

A python application using the [flasgger](https://github.com/flasgger/flasgger) framework to manage game sessions of [citadels](https://boardgamegeek.com/boardgame/478/citadels).

This is a little project to test my python programming skills and to create a way for people to play this game online with friends since there is no official way to do so at the moment. **This project is in no way intended for commercial purposes**.

The goal was to create an application which could run on a server or someone's PC where players could create game sessions and other players could join to play through their web browser.

This API is used together with the [citadels client](https://github.com/benblanc/citadels-client), which is an application which allows you to play the game through your browser.

I hope everyone has fun playing this wonderful game together!

## Getting started

[Open a terminal](https://atom.io/packages/open-terminal-here) at the location of this cloned/downloaded repository and run these commands:

1. Start the [database](https://dbdiagram.io/d/61bcfbdf3205b45b73c33207) (and wait +- 30 seconds):
    ``` bash
    docker-compose up -d
    ```

2. Create a virtual environment, if it doesn't exist:
    ``` bash
    python3 -m venv ./venv
    ```

3. Activate the virtual environment:
    ``` bash
    source venv/bin/activate
    ```

4. Install the required packages:
    ``` bash
    pip install -r requirements.txt
    ```

5. Set the environment:
    ``` bash
    export PYTHON_ENV=local 
    ```

6. Run the application:
    ``` bash
    python main.py
    ```

While the application is running, people can play games using the [citadels client](https://github.com/benblanc/citadels-client).

While the application is running, you can view all of the API's endpoints by going to this URL:

``` text
http://127.0.0.1:8080/apidocs
```

### Prerequisites

This application was programmed using [python 3.7](https://www.python.org/downloads/release/python-3712/):

* If you have python 3 installed on your system, try using that first
* If you don't have python installed on your system, download python 3.7

This application also uses [docker-compose](https://docs.docker.com/compose/) to manage a mysql database. If you don't have docker-compose installed on your system, you can follow [these steps](https://docs.docker.com/compose/install/#install-compose) to install it on your system. You can also install just install the mysql database separately, but you'll have to find out how on your own.

## Running the tests

The API has a script which simulates a game from start to finish testing whether all endpoints work as intended.

There is also a script to test if scores are calculated correctly, but this one isn't that important (and may be outdated).

These scripts **require** the API to be running in the background.

### Simulate game

[Open a terminal](https://atom.io/packages/open-terminal-here) at the location of this cloned/downloaded repository and run these commands:

1. Activate the virtual environment used for the API:
    ``` bash
    source venv/bin/activate
    ```

2. Run the application:
    ``` bash
    python ./tests/simulate_game/run.py
    ```

The script will make requests to the endpoints of the API to simulate a game. The final output of the script will let you know the game has finished.

### Calculate scores

[Open a terminal](https://atom.io/packages/open-terminal-here) at the location of this cloned/downloaded repository and run these commands:

1. Activate the virtual environment used for the API:
    ``` bash
    source venv/bin/activate
    ```

2. Run the application:
    ``` bash
    python ./tests/calculate_scores.py
    ```

The final output should be the score each player has in the database and the score the script calculated.

## Notes

The game only uses the cards from the original set, except for the graveyard and the great wall.

Programming the graveyard would have been difficult/annoying, so I replaced it with the great wall which was easier to programme.
