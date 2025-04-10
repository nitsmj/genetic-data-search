from flask import Flask, request, render_template, redirect, url_for, flash
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'.xlsx', '.tsv', '.csv'}

def allowed_file(filename):
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('excel')
    uploaded_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            counter = 1
            base, ext = os.path.splitext(file.filename)
            while os.path.exists(filepath):
                filepath = os.path.join(UPLOAD_FOLDER, f"{base}_{counter}{ext}")
                counter += 1
            file.save(filepath)
            uploaded_files.append(os.path.basename(filepath))

    if uploaded_files:
        flash(f"{len(uploaded_files)} file(s) uploaded successfully!")
    else:
        flash("No valid files uploaded.")
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    results = []

    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if filename.endswith('.xlsx'):
                    df = pd.read_excel(filepath)
                elif filename.endswith('.tsv'):
                    df = pd.read_csv(filepath, sep='\t')
                elif filename.endswith('.csv'):
                    df = pd.read_csv(filepath)

                for index, row in df.iterrows():
                    for cell in row:
                        if pd.notna(cell) and query in str(cell).lower():
                            results.append({'file': filename, 'row': row.to_dict()})
                            break
            except Exception as e:
                results.append({'file': filename, 'error': str(e)})

    flash(f"Search completed! Found {len(results)} match(es)." if results else "No matches found.")
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)

