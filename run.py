
import os
print("=== DATABASE_URL ===", os.environ.get('DATABASE_URL', 'NOT SET'))
print("=== FLASK_APP ===", os.environ.get('FLASK_APP', 'NOT SET'))

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
