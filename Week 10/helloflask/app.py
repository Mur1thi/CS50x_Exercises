from flask import Flask, render_template, request

app = Flask(__name__)

valid_colors = ["red", "blue"]

"""
Validates a given color.

Args:
    color (str): The color to be validated.

Returns:
    str: The rendered template based on whether the color is valid or not.
"""


def validate_color(color):
    if color in valid_colors:
        return render_template("color.html", color=color)
    else:
        return render_template("error.html", color=color)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    This function handles the root route of the application.

    If the request method is GET, it renders the index.html template.
    If the request method is POST, it retrieves the 'color' value from the form,
    and renders the color.html template with the 'color' value.

    Returns:
        str: The rendered HTML template for the index page (index.html)
            if the request method is GET.
        str: The rendered HTML template for the color page (color.html)
            with the 'color' value if the request method is POST.
    """
    if request.method == "GET":
        return render_template("index.html")
    else:
        print("Form submitted")
        color = request.form.get("color")
        return validate_color(color)
