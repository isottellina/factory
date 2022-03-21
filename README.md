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

## Troubleshooting
This project was tested on Linux, and compatibility is not guaranteed for other platforms.

The error "can't find an installation candidate" is due to your system not corresponding to
any binary distributions (wheels) given for Shiboken6. They are available for manylinux1 (so, using
Linux you shouldn't have problems), Windows 64-bits (not cygwin), and macOS X 10.14 (and maybe later
versions, I haven't been able to test as I have no Mac system). If you find yourself in one of these
cases, you're going to have to build Shiboken6 and PySide6 from source. You can find instructions here:
https://doc.qt.io/qtforpython/gettingstarted.html

You can also try the qt5 branch, which uses Qt5 and could have wheels for a few more platforms, such as
Windows 32-bits or macOS X 10.13.

Despite using qt6, this project can run on systems on which it is not available (i.e. Debian stable).
However, you might need to install libraries, of which we can't provide a complete list. The environment
variable QT_DEBUG_PLUGINS might be useful for this, since it will print out which libraries Qt can't
load.

## Contributing
Pull requests are welcome. In terms of code-style, this project uses black, isort, mypy and flake8.
Make sure your code is compliant before submitting it. To help you, pre-commit hooks are set-up.
You can enable them by running `poetry run pre-commit install`.
