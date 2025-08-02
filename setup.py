from setuptools import setup

APP = ['app.py']  # your main Python script
DATA_FILES = ['templates', 'uploads', 'trd_public.json']  # folders/files your app uses
OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'flask',
        'flask_cors',
        'uuid',
        'zipfile',
        'pathlib',
        'json',
        'threading',
        'werkzeug.utils',
        'os',
        'time',
        'jaraco.text',  # 🧠 ADD THIS
    ],
    'packages': ['flask', 'flask_cors', 'jaraco'],
    'resources': ['templates'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
v