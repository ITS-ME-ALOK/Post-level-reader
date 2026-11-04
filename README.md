# Post level reader / PDF To Excel Converter

This application reads multi-page PDF files, extracts post level structural blocks using regular expressions, and generates transformed Excel files ready for consumption.

## Architecture
- `main.py`: Application entry point.
- `ui/`: Modern CustomTkinter User Interface components.
- `services/`: Core decoupled business logic classes (`pdf_reader`, `parser`, `transformer`, `excel_generator`).
- `utils/`: Logging configuration and application constants.
- `assets/`, `logs/`, `output/`: Application runtime directories.

## Requirements
- Python 3.12
- Dependencies listed in `requirements.txt`

## Running the Application Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Building for Production
A `build.bat` script is included to generate a standalone Windows Executable.
To build it manually:
```bash
pyinstaller --onefile --windowed main.py
```
The resulting executable will be placed in the `dist/` folder.
