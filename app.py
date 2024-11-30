from flask import Flask
from flask_mysqldb import MySQL
import google.generativeai
import os
from dotenv import load_dotenv
import markdown
from markupsafe import Markup

app = Flask(__name__)

def markdown_filter(text):
    return Markup(markdown.markdown(text))
app.jinja_env.filters.update(markdown=markdown_filter)


MYSQL_DB = 'user_accounts'
CODE_CHAT_MODEL = "gemini-pro"
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
PROJECT_ID = os.environ.get('PROJECT_ID')


dao = MySQL(app)
google.generativeai.configure(api_key=GOOGLE_APPLICATION_CREDENTIALS)
model = google.generativeai.GenerativeModel(CODE_CHAT_MODEL)
chat_config = {
    "max_output_tokens": 2048,
    "temperature": 0.9,
    "top_p": 1
}
# max_output_tokens: The maximum number of tokens to generate in the output.
# temperature: The temperature to use when sampling from the model. Higher values will result in more random outputs.
# top_p: The cumulative probability threshold to use when sampling from the model. Lower values will result in more random outputs.



# # Import routes
from routes.user import user
from routes.portfolio import portfolio

# Register blueprints

app.register_blueprint(user)
app.register_blueprint(portfolio)

if __name__ == "__main__":
    app.run(debug=True)
