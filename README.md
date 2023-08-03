Codexium

Codexium is a simple web application for uploading and searching text files. Built with Python and Flask, it utilizes SQLite's full-text search (FTS5) for efficient and effective text search. With an intuitive and user-friendly interface, Codexium provides an easy way to manage and search a collection of text files.

Features
File Upload: Supports uploading .txt, .pdf, and .zip files containing them. Identically named files will be replaced.
Full-Text Search: Uses SQLite's full-text search (FTS5) to quickly search the content of uploaded files.
Search Snippets: Provides snippets of text from each file where the search terms appear.
File Preview: Allows users to view the full content of any uploaded file.
Pagination: Paginated search results for better usability.

Installation
Clone the repository:
```
git clone https://github.com/yourusername/codexium.git
```
Change directory to the project folder:
```
cd codexium
```
Install the required Python packages:
```
pip install -r requirements.txt
```
Run the application:
```
python app.py
```
Open a web browser and navigate to http://localhost:5000.

Usage
Upload a file: Click on 'Go to Upload' and drop a file into the upload area or click the area to select a file from your device.
Search: Enter your search terms into the search bar and click 'Search'.
View a file: Click on a file name in the search results to view its full content.

Future Improvements
Implement user authentication to allow each user to have their own collection of files.
Add support for more file types.
Improve the interface with a modern front-end framework.
