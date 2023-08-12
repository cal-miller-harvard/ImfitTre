"""Application entry point."""
from imfittre import init_app
from asyncio import run

app = run(init_app())

if __name__ == "__main__":
    app.run()