from flask import Flask, render_template, request, send_file
import pandas as pd
from search import search_excel

app = Flask(__name__)

# Route to serve your HTML page
@app.route("/", methods=["GET"])
def home():
    query = request.args.get("query")
    results = None
    if query:
        results = search_excel(query)
        if results.empty:
            results = None
    return render_template("index.html", results=results, query=query)



if __name__ == "__main__":
    app.run(debug=True)
