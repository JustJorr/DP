from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Kenzy <3 Gerald oh yeah baby'

if __name__ == '__main__':
    app.run(debug=True)
