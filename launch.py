# -*- coding: utf-8 -*-

"""Application entry point."""
from project import create_app
import os

app = create_app()
env = os.environ['WORK_DIR']

if __name__ == "__main__":
    if env == 'local':
        app.run(debug=True)
    elif env == 'docker':
        app.run(debug=True, host='0.0.0.0')



