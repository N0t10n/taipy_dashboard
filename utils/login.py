from taipy.gui import Gui, notify


login_open = True
username = ''
password = ''


dialog_md = """
<|{login_open}|dialog|title=Login|labels=Create account|on_action=create_account|width=30%|
**Username**
<|{username}|input|label=Username|class_name=fullwidth|>

**Password**
<|{password}|input|password|label=Password|class_name=fullwidth|>

<br/>
<|Sign in|button|class_name=fullwidth plain|on_action=login|>
|>
"""


def create_account(state):
    notify(state, "info", "Creating account...")
    # Put your own logic to create an account
    # Maybe, by opening another dialog
    state.username = "Taipy"
    state.password = "password"
    notify(state, "success", "Account created!")


def login(state):
    # Put your own authentication system here
    if state.username == "Taipy" and state.password == "password":
        state.login_open = False
        notify(state, "success", "Logged in!")
    else:
        notify(state, "error", "Wrong username or password!")


pages = {"/": dialog_md,
         "Home": "# Taipy application"}

if __name__ == "__main__":
    Gui(pages=pages).run()