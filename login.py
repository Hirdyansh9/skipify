from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = '123456'  # Necessary for session management

# Sample username and password for demonstration purposes
USERNAME = 'admin'
PASSWORD = 'password'


@app.route('/')
def home():
    # Redirect to main page if already logged in
    if 'username' in session:
        return redirect(url_for('main'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the credentials match
        if username == USERNAME and password == PASSWORD:
            session['username'] = username  # Save username in session
            return redirect(url_for('main'))
        else:
            return 'Invalid Credentials. Please try again.'

    return render_template('login.html')


@app.route('/main')
def main():
    # Check if the user is logged in
    if 'username' in session:
        return f'Hello, {session["username"]}! Welcome to the main page.'
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
