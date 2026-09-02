"""Allow Foco to run with ``python -m foco``."""

from .main import FocoApp


def main():
    FocoApp().run()


if __name__ == "__main__":
    main()
