from pathlib import Path

app_file = Path(__file__).parent / "app" / "app.py"

exec(
    compile(app_file.read_text(), str(app_file), "exec"),
    {
        "__file__": str(app_file),
        "__name__": "__main__",
    },
)