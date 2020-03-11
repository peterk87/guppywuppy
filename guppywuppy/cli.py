"""Console script for guppywuppy."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for guppywuppy."""
    from guppywuppy.app import app
    app.run(host="0.0.0.0", port=8000, debug=True, access_log=True)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
