from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader
import sqlite3
import os
import zipfile
import io
import re
from urllib.parse import unquote
from tqdm import tqdm
app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('codexes\sites.db', check_same_thread=False)

# Create a cursor
c = conn.cursor()
# Create the 'documents' table if it does not exist
c.execute('''
CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(id, content);
''')
conn.commit()
def snippet_maker(data, pattern, max_tokens):
    pattern_lower = pattern.lower()
    snippets = []
    for item in data:
        item_lower = item.lower()
        match = re.search(pattern_lower, item_lower)
        if match:
            tokens = item.split()
            tokens_lower = item_lower.split()
            
            # Find the match start and end in the token list
            pattern_tokens = pattern_lower.split()
            match_start, match_end = None, None
            for i in range(len(tokens_lower) - len(pattern_tokens) + 1):
                if tokens_lower[i:i+len(pattern_tokens)] == pattern_tokens:
                    match_start, match_end = i, i + len(pattern_tokens)
                    break

            if match_start is not None and match_end is not None:
                start = max(0, match_start - max_tokens)
                end = min(len(tokens), match_end + max_tokens)
                snippet = " ".join(tokens[start:end])
                snippets.append(snippet)
    return snippets


def extract_text_from_pdf(file):
    pdf = PdfFileReader(file)
    text = " ".join(page.extract_text() for page in pdf.pages)
    return text
    

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        files = request.files.getlist('file')

        for file in files:
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)
            if filename.endswith('.pdf'):
                content = extract_text_from_pdf(file)
                # Insert the document into the SQLite database
                c.execute('''
                    INSERT OR REPLACE INTO documents (id, content) VALUES (?, ?);
                ''', (filename, content))

            elif filename.endswith('.zip'):
                z = zipfile.ZipFile(file)
                for name in tqdm(z.namelist()):
                    try:
                        if name.endswith('.pdf'):
                            content = extract_text_from_pdf(io.BytesIO(z.read(name)))
                            filename = name
                            # Insert the document into the SQLite database
                            c.execute('''
                                INSERT OR REPLACE INTO documents (id, content) VALUES (?, ?);
                            ''', (filename, content))

                        else:
                            content = z.read(name).decode('utf-8')
                            filename = name
                            # Insert the document into the SQLite database
                            c.execute('''
                                INSERT OR REPLACE INTO documents (id, content) VALUES (?, ?);
                            ''', (filename, content))

                    except:
                        pass
            else:
                content = file.read().decode('utf-8')

                # Insert the document into the SQLite database
                c.execute('''
                    INSERT OR REPLACE INTO documents (id, content) VALUES (?, ?);
                ''', (filename, content))
            conn.commit()

        return jsonify({'message': 'Files successfully uploaded'}), 200
    return render_template('upload.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query_str = request.form['q']
        page = int(request.form.get('page', 1))  # Get the page number from form data, default to 1
    else:
        return render_template('search.html', results=None)

    results_per_page = int(request.args.get('results_per_page', 10))  # Get the number of results per page, default to 10
    offset = (page - 1) * results_per_page  # Calculate the offset

    if not query_str:
        return jsonify({'error': 'Missing query parameter'}), 400

    # Perform a full-text search with limit and offset
    c.execute('''
        SELECT id, content FROM documents WHERE documents MATCH ? LIMIT ? OFFSET ?;
    ''', (query_str, results_per_page, offset))

    # Fetch the results
    results = c.fetchall()

    # Calculate the total number of results and pages
    c.execute('''
        SELECT COUNT(*) FROM documents WHERE documents MATCH ?;
    ''', (query_str,))
    total_results = c.fetchone()[0]
    num_pages = -(-total_results // results_per_page)  # Ceil division

    if not results:
        return render_template('search.html', message="No results found.")
    else:
        # Generate snippets for each result
        snippets = {}
        for id, content in results:
            snippets[id] = snippet_maker([content], query_str, 250)

        return render_template('search.html', results=[id for id, _ in results], snippets=snippets, page=page, num_pages=num_pages, query_str=query_str)


@app.route('/file/<path:filename>', methods=['GET'])
def file(filename):
    filename = unquote(filename)
    # Fetch the file content from the database
    c.execute('''
        SELECT content FROM documents WHERE id = ?;
    ''', (filename,))

    # Fetch the result
    result = c.fetchone()

    if result is None:
        return "File not found", 404

    content = result[0]

    # Render the content in a new HTML template
    return render_template('file.html', filename=filename, content=content)

if __name__ == '__main__':
    app.run(debug=True)
