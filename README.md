# Citadels API

Link to database schema: https://dbdiagram.io/d/61bcfbdf3205b45b73c33207

---

A python application using the [flasgger](https://github.com/flasgger/flasgger) framework to manage one or more game sessions of [citadels](https://boardgamegeek.com/boardgame/478/citadels).

This is a little project to test my python programming skills and to create a way for people to play this game online with friends since there is no official way to at the moment. **This project is in no way intended for commercial purposes**.

The goal was to create an application which could run on a server where players could create game sessions and other players could join to play through their web browser.

This API is used together with the [citadels client](https://github.com/benblanc/citadels-client), which is an application which allows you to play the game through your browser.

## Getting Started

[Open a terminal](https://atom.io/packages/open-terminal-here) at the location of this cloned/downloaded repository and run these commands:

1. Start the database (and wait +- 30 seconds):
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

### Prerequisites

This application was programmed using [python 3.7](https://www.python.org/downloads/release/python-3712/):

* If you have python 3 installed on your system, try using that first
* If you don't have python installed on your system, then download python 3.7

### Installing

A step by step series of examples that tell you how to get a development environment running

Say what the step will be

    Give the example

And repeat

    until finished

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Sample Tests

Explain what these tests test and why

    Give an example

### Style test

Checks if the best practices and the right coding style has been used.

    Give an example

## Deployment

Add additional notes to deploy this on a live system

## Built With

- [Contributor Covenant](https://www.contributor-covenant.org/) - Used for the Code of Conduct
- [Creative Commons](https://creativecommons.org/) - Used to choose the license

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/PurpleBooth/a-good-readme-template/tags).

## Authors

- **Billie Thompson** - *Provided README Template* -
  [PurpleBooth](https://github.com/PurpleBooth)

See also the list of
[contributors](https://github.com/PurpleBooth/a-good-readme-template/contributors)
who participated in this project.

## License

This project is licensed under the [CC0 1.0 Universal](LICENSE.md)
Creative Commons License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- Hat tip to anyone whose code is used
- Inspiration
- etc