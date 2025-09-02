from flask import Flask, render_template_string, request, session, redirect, url_for
import uuid

app = Flask(__name__)
app.secret_key = "supersecret"  # 🔒 Change this in production

# Track active users by email: { email: session_id }
active_users = {}

# Replace with your actual Microsoft Forms quiz link
QUIZ_LINK = "https://forms.office.com/Pages/ResponsePage.aspx?id=s-7mYddfqkquPGHo3rCbebdvsmz8y_VMkCAeEiT0GeZUQkVNOEZSSFc5QjJJWTVKV1ZOQ0JJRDZYVy4u"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        session_id = str(uuid.uuid4())  # unique session

        # Kick out any previous login for same email
        active_users[email] = session_id
        session["email"] = email
        session["session_id"] = session_id

        return redirect("/quiz")

    return '''
        <h2>Enter your email to start the quiz</h2>
        <form method="post">
            <input type="email" name="email" required placeholder="Enter email">
            <input type="submit" value="Start Quiz">
        </form>
    '''


@app.route("/quiz")
def quiz():
    if "email" not in session or "session_id" not in session:
        return redirect("/")

    email = session["email"]
    session_id = session["session_id"]

    # Check if user has been logged out (another login with same email)
    if active_users.get(email) != session_id:
        session.clear()
        return "<h3>You have been logged out because you logged in from another browser.</h3><a href='/'>Login again</a>"

    # HTML with fullscreen + close test button
    html_content = f"""
    <h2>Quiz for {email}</h2>
    <button onclick="startTest()">Start Test in Fullscreen</button>
    <button onclick="closeTest()">Close Test</button>

    <div id="quizContainer" style="display:none;">
      <iframe src="{QUIZ_LINK}" width="100%" height="700px" style="border:none;"></iframe>
    </div>

    <script>
      function startTest() {{
        let elem = document.documentElement;
        if (elem.requestFullscreen) {{
          elem.requestFullscreen();
        }}
        document.getElementById("quizContainer").style.display = "block";
      }}

      function closeTest() {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }}
        window.location.href = "/logout";
      }}

      // Detect tab switching
      document.addEventListener("visibilitychange", () => {{
        if (document.hidden) {{
          alert("Switching tabs is not allowed!");
        }}
      }});

      // Disable right-click
      document.addEventListener('contextmenu', event => event.preventDefault());

      // Disable copy/paste
      document.addEventListener('copy', e => e.preventDefault());
      document.addEventListener('paste', e => e.preventDefault());
    </script>

    <br><a href="/logout">Logout</a>
    """
    return render_template_string(html_content)


@app.route("/logout")
def logout():
    email = session.pop("email", None)
    session_id = session.pop("session_id", None)
    if email and active_users.get(email) == session_id:
        active_users.pop(email, None)  # only clear if still their session
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
