from flask import Flask, render_template_string, request, session

app = Flask(__name__)
app.secret_key = "demo-only-not-for-prod"


PAGE_TEMPLATE = """
<!doctype html>
<title>Inventory Lookup</title>
<h1>Hello, {{ name|e }}</h1>
<form method=post>
  <input name=item placeholder="item id">
  <button type=submit>Look up</button>
</form>
{% if last %}<p>Last item looked up: {{ last|e }}</p>{% endif %}
"""


@app.get("/")
def index():
    return render_template_string(PAGE_TEMPLATE, name=session.get("user", "guest"), last=session.get("last"))


@app.post("/")
def submit():
    item = request.form.get("item", "").strip()
    if item:
        session["last"] = item
    return render_template_string(PAGE_TEMPLATE, name=session.get("user", "guest"), last=session.get("last"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
