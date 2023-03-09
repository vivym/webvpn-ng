import typer

from .chisel import Chisel
from .login import login as _login, check_login, get_cookie, get_token, get_server

app = typer.Typer(no_args_is_help=True)


@app.command()
def login(
    username: str,
    password: str = typer.Option(..., prompt=True, hide_input=True),
    token: str = typer.Option("", prompt=True),
):
    if len(token) > 0 and ":" not in token:
        typer.echo("Invalid token")
        return

    typer.echo(f"Logging in {username}")

    if _login(username, password, token):
        typer.echo("Login success")
    else:
        typer.echo("Login failed")


@app.command()
def forward(
    host: str = "localhost",
    port: int = "2222",
    rhost: str = "10.251.0.23",
    rport: int = "22",
    delay: int = 100,
    quiet: bool = False,
):
    if not check_login():
        typer.echo("Not logged in")
        return

    typer.echo(f"Forwarding {host}:{port} -> {rhost}:{rport}")

    token = get_token()

    typer.echo("Getting server url... ", nl=False)
    server = get_server(token)
    if not server:
        typer.echo("Failed to get server.")
        return
    else:
        typer.echo("Done.")

    chisel = Chisel(
        server=server,
        cookie=get_cookie(),
        local_host=host,
        local_port=port,
        remote_host=rhost,
        remote_port=rport,
        auth_key=token,
        delay=delay,
        quiet=quiet,
    )
    chisel.run()


if __name__ == "__main__":
    app()
