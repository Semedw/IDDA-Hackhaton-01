# IDE Setup Guide

This guide helps configure your IDE to properly resolve Django modules.

## VS Code / Cursor Setup

1. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose: `./backend/venv/bin/python`

2. **Reload Window:**
   - Press `Ctrl+Shift+P`
   - Type "Developer: Reload Window"

3. **Verify Configuration:**
   - The `.vscode/settings.json` file is already configured
   - It points to the virtual environment at `backend/venv`

## PyCharm Setup

1. **Open Project Settings:**
   - File → Settings → Project → Python Interpreter

2. **Add Interpreter:**
   - Click the gear icon → Add
   - Select "Existing Environment"
   - Path: `./backend/venv/bin/python`

3. **Set Project Root:**
   - File → Settings → Project Structure
   - Mark `backend` as Sources Root

## Pyright / Pylance Configuration

The project includes:
- `pyrightconfig.json` - Pyright configuration
- `pyproject.toml` - Python project configuration
- `.python-version` - Python version specification

These files tell the type checker:
- Where the virtual environment is (`backend/venv`)
- Which Python version to use (3.12)
- Which directories to include/exclude

## Manual Python Path Setup

If modules still aren't resolving, add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

Or activate the virtual environment:
```bash
source backend/venv/bin/activate
```

## Troubleshooting

### "Django module not found"
1. Ensure virtual environment is activated
2. Verify Django is installed: `pip list | grep Django`
3. Check Python interpreter in IDE settings
4. Reload IDE window

### "Import errors in IDE but code runs"
- This is usually an IDE configuration issue
- The code will still run correctly
- Follow the IDE setup steps above

### Verify Setup
```bash
cd backend
source venv/bin/activate
python -c "import django; print('Django version:', django.get_version())"
```

If this works, Django is installed correctly. The IDE just needs to be configured to use the same interpreter.

