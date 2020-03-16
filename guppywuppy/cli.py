"""Console script for guppywuppy."""
import sys
import click


@click.command()
@click.option('-p', '--port', type=int, default=8000, help='Port to serve app at')
@click.option('-h', '--host', type=str, default='0.0.0.0', help='Host to serve app at')
@click.option('--debug', is_flag=True, help='Debug mode')
@click.option('--access-log', is_flag=True, help='Enable access log?')
def main(port, host, debug, access_log):
    """Console script for guppywuppy."""
    from guppywuppy.app import app
    app.run(host=host,
            port=port,
            debug=debug,
            access_log=access_log)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
