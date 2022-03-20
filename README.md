# Factory

Factory is a game about robots making ressources, called Foos and Bars. With these
ressources, they can make Foobars, which they can then sell to have money.

You win by obtaining your 30th robot.

## Poetry
This project is managed by poetry, and therefore you need Poetry. You can find all about how to
install it by following this link: https://python-poetry.org/docs/#installation

## Running
Once you have installed poetry, you need to setup a virtual environment and then you can run the
game. Both of these steps are done by:

```
poetry install
poetry run factory
```

On UNIX-based systems, make sure Qt6 and libclang are available as shared libraries.

## Troubleshooting
This project was tested on Linux, and compatibility is not guaranteed for other platforms.
However, issues running this program are probably due to PySide6 or Shiboken6 (from the Qt for Python
project). You can read instructions on how to build it on different platforms here:
https://doc.qt.io/qtforpython/gettingstarted.html


## Contributing
Pull requests are welcome. In terms of code-style, this project uses black, isort, mypy and flake8.
Make sure your code is compliant before submitting it. To help you, pre-commit hooks are set-up.
You can enable them by running `poetry run pre-commit install`.
