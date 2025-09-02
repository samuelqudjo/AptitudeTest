from flask import Flask, render_template_string, request, session, redirect
import uuid

app = Flask(__name__)
app.secret_key = "supersecret"  # Change in production

# Store active users: { email: session_id }
active_users = {}

# Replace with your Microsoft Forms quiz link
QUIZ_LINK = "https://forms.office.com/Pages/ResponsePage.aspx?id=s-7mYddfqkquPGHo3rCbebdvsmz8y_VMkCAeEiT0GeZUQkVNOEZSSFc5QjJJWTVKV1ZOQ0JJRDZYVy4u"

# -------------------------------
# Login Page
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        session_id = str(uuid.uuid4())  # generate unique session ID

        # Store new session, kicking out old one if exists
        active_users[email] = session_id
        session["email"] = email
        session["session_id"] = session_id

        return redirect("/quiz")

    # Show login form
    return '''
        <h2>Enter your email to start the quiz</h2>
        <form method="post">
            <input type="email" name="email" required placeholder="Enter email">
            <input type="submit" value="Start Quiz">
        </form>
    '''

# -------------------------------
# Quiz Page
# -------------------------------
@app.route("/quiz")
def quiz():
    if "email" not in session or "session_id" not in session:
        return redirect("/")

    email = session["email"]
    session_id = session["session_id"]

    # If user was kicked out (new login with same email elsewhere)
    if active_users.get(email) != session_id:
        session.clear()
        return "<h3>You have been logged out because you logged in from another browser.</h3><a href='/'>Login again</a>"

    # HTML + JS restrictions
    html_content = f"""
    <h2>Quiz for {email}</h2>
    <button onclick="openFullscreen()">Start Fullscreen & Begin Test</button>
    <br><br>
    <iframe id="quizFrame" src="{QUIZ_LINK}" width="100%" height="700px" style="border:none; display:none;"></iframe>
    <br>
    <button id="finishBtn" onclick="finishTest()" style="display:none;">Finish Test</button>

    <script>
      let quizFrame = document.getElementById("quizFrame");
      let finishBtn = document.getElementById("finishBtn");

      // Force fullscreen
      function openFullscreen() {{
        let elem = document.documentElement;
        if (elem.requestFullscreen) {{
          elem.requestFullscreen();
        }}
        quizFrame.style.display = "block";
        finishBtn.style.display = "inline-block";
      }}

      // Exit fullscreen + logout
      function finishTest() {{
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

      // Detect if fullscreen is exited (kick them out)
      document.addEventListener("fullscreenchange", () => {{
        if (!document.fullscreenElement) {{
          alert("You exited fullscreen. Test ended.");
          window.location.href = "/logout";
        }}
      }});

      // Disable right-click
      document.addEventListener('contextmenu', event => event.preventDefault());

      // Disable copy/paste
      document.addEventListener('copy', e => e.preventDefault());
      document.addEventListener('paste', e => e.preventDefault());
    </script>
    """
    return render_template_string(html_content)

# -------------------------------
# Logout
# -------------------------------
@app.route("/logout")
def logout():
    email = session.pop("email", None)
    session_id = session.pop("session_id", None)

    # Only remove if still their active session
    if email and active_users.get(email) == session_id:
        active_users.pop(email, None)

    return "<h3>You have logged out successfully.</h3><a href='/'>Login again</a>"

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
