CNG445 Assignment 3 (Local Event Advertisement Portal)

1. Team Members
    Alperen Kayhan - 2385532
    Semir Emre Gedikli - 2526333

2. Python Version
    -Python 3.10.

3. Operating System
    The program was developed and tested on:
        - Windows 11
        - macOS Tahoe 26.1

4.Teamwork, Communication and Testing

Task Distribution:

    Semir Emre Gedikli (2526333):
        - Html templates (base, index, events, search, societies, profile, event detail, 		register ok)
        - css file (static/style.css)
        - js validation file (static/validation.js) (password check + event fee + profile checks 	- fee box toggle)
        - Tested the menu links (admin should see manage societies, users see announced events) 	and general UI flow

    Alperen Kayhan (2385532):
        - Wrote the Flask app (app.py) and the routes (login, register, events, delete, 		societies, profile, search, see more)
        - Did the sqlite queries + session stuff + restrictions (admin vs normal user)
        - Server side checks like password rule, fee conversion, required fields, unique errors

* We talked mostly in person and also messaged each other when something broke. We shared the files in a shared folder so we don’t lose versions. Thus, we are in the direct contact and, 
as a team we help each other. Task distribution in this context to describe which one is the supervisor of which section.

Testing:
    The program was tested by:
        - Registered with wrong passwords (too short, no uppercase, no digit) and checked it 		blocks
        - Tried duplicate username to see error
        - Login with wrong username / wrong password / correct one
        - Checked admin cannot open /events (it redirects to societies)
        - Added societies: empty input, duplicate name, normal input
        - Created events: missing fields, no society ticked, paid fee invalid like “abc”, paid 		fee valid like “50.5”, free event (fee NULL)
        - Delete event button only deletes the owner’s event
	- Search: single society and ALL societies, multiple keywords, also checked “See More” 		opens the detail page with societies list and fee as Free/number