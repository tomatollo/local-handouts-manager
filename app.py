from flask import Flask, render_template

app = Flask(__name__)

# Players 
@app.route('/')
def home():
    return render_template('player_hub.html')

# Master
@app.route('/dm-panel')
def dm_panel():
    return render_template('master_dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)