# Factory

## Running
This game and its dependency management requires Poetry. To play it, you first have to set up
a virtual environment. Then you can run the program. Both of these steps are done by running:

```
poetry install
poetry run factory
```

On UNIX-based systems, make sure Qt6 and libclang are available as shared libraries.

## Troubleshooting
This project was tested on Linux, and compatibility is not guaranteed for other platforms.
However, issues running this program are probably due to PySide6. You can read instructions
on how to run it on different platforms [here](https://doc.qt.io/qtforpython/gettingstarted.html).


## Contributing
Pull requests are welcome. In terms of code-style, this project uses black, isort, mypy and flake8.
Make sure your code is compliant before submitting it. To help you, pre-commit hooks are set-up.
You can enable them by running `poetry run pre-commit install`.

Note: Pre-commit hooks don't run mypy. It will, however, be checked by the CI.
