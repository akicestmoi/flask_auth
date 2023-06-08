# flask_auth

## Stack
This API is based on Python Flask library and uses PostgreSQL as databases. It also uses Flask-SQLAlchemy as ORM and Pytest for Unit Testing. It also uses: Flask-Bcrypt for password hashing, Flask-login for session management.
It is designed following the Flask Factory Pattern in order to enhance the project modularity in case the projet expands.

## Database Schema
The table on which the API relies on is designed as follows:
- *id*: integer. Primary Key, auto filled by SQLAlchemy.
- *email*: string. Required field. Has to be unique.
- *username*: string. Required field. Has to be unique.
- *password*: string. Required field. Hashed based on Flask-Bcrypt algorithm. Must contain at least 6 characters, 1 Upper case, 1 Lower case, 1 numerical character, 1 Special character.
- *gender*: string. Optional field, None by default.
- *phone_number*: string. Optional field, None by default.
- *address*: string. string. Optional field, None by default.
- *is_logged_in*: boolean. Auto-filled by the API upon creation to True. Indicates account status for Front-End session management.

## Functionnality
The project is a backend server providing APIs for authentication, including the following functionality:
- Password hashing, using Flask-Bcrypt.
- Password restriction (at least 6 characters, 1 Upper case, 1 Lower case, 1 numerical character, 1 Special character).
- Email and Username unicity check.
- Session management based on Flask-login. Once credentials are validated by the API, flask-login creates a session cookie.
- Signup, based on 3 required fields (email, username and password) and 3 optional fields (gender, phone_number, and address). The optionality is automatically taken care of if not included in the POST body.
- Login, based on 2 required fields (username and password). It compares the hashed password stored in the database and the userinput, and allows access once password passes Bcrypt validity check. Modify account status to "is_logged_in" = True.
- Logout, Modify account status to "is_logged_in" = False.
- Modify Account field, can modify any field of the specified Account. Note: an additionnal security step is included when modifying password : password modification is enabled only if the PATCH body contains a specific parameter called: "password_validation", which should contain the value of the previous password.
- Reset optional fields, reset all 3 optional fields (gender, phone_number, and address) to its default value e.g. None.
- Delete account.
- Access the content of the entire database.
- Access the data of one specific account.

## Available Routes
- /
- /db-content (GET)
- /accounts/<id> (GET, PUT, DELETE, PATCH + body: [field to modify (include "password_validation" with original password to modify "password")])
- /signup (POST + body: [Required field, Optional field])
- /login (POST + body: [username, password])
- /home (login is required)
- /logout/<id> (POST, login is required)