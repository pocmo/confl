# Installation

## Requirements

- Python 3.11 or higher
- pip or pipx

## Installing with pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs Python CLI tools in isolated environments:

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install confl
pipx install git+https://github.com/pocmo/confl.git

# Verify installation
confl --help
```

### Upgrading

```bash
pipx upgrade confl
```

### Uninstalling

```bash
pipx uninstall confl
```

## Installing with pip

You can also install with pip, though pipx is preferred:

```bash
pip install git+https://github.com/pocmo/confl.git
```

**Note:** This installs `confl` globally in your Python environment. Consider using a virtual environment or pipx to avoid conflicts.

## Installing from Source

For development or to run from source:

```bash
# Clone the repository
git clone https://github.com/pocmo/confl.git
cd confl

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run confl
uv run confl --help
```

## Shell Completion

`confl` supports shell completion for bash, zsh, and fish:

```bash
# Install completion for your shell
confl --install-completion

# Show completion script (for manual setup)
confl --show-completion
```

After installing completion, restart your shell or source your shell config file.

## Troubleshooting

### Command not found

If you get "command not found" after installing with pipx:

1. Make sure pipx's bin directory is in your PATH:
   ```bash
   python3 -m pipx ensurepath
   ```

2. Restart your shell or source your shell config

3. Check if confl is installed:
   ```bash
   pipx list
   ```

### Permission errors

If you get permission errors during installation:

- Use pipx (recommended) — it installs in your user directory
- Or use pip with `--user` flag: `pip install --user git+https://github.com/pocmo/confl.git`
- Don't use `sudo pip install` — this can break your system Python

### Python version too old

`confl` requires Python 3.11 or higher. Check your version:

```bash
python3 --version
```

If your version is too old, install a newer Python version using:
- **macOS**: Homebrew (`brew install python@3.11`)
- **Ubuntu/Debian**: `sudo apt install python3.11`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

## Next Steps

After installation, see:
- [Getting Started Guide](getting-started.md) — Step-by-step setup walkthrough
- [Authentication](authentication.md) — Setting up API tokens
- [Commands](commands.md) — Complete command reference

## See Also

- [GitHub Repository](https://github.com/pocmo/confl)
- [Configuration](configuration.md) — Config files and profiles
