import sqlite3

# DB file name
DB_NAME = "portal.db"

def createDatabase():
    # connect to the database file
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # enable foreign key constraints
    c.execute("PRAGMA foreign_keys = ON;")

    # USERS TABLE:
    # username is unique identifier (PK).
    # is_admin is 0 or 1 only (so normal user or admin)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username   TEXT PRIMARY KEY,
        password   TEXT NOT NULL,
        fullname   TEXT NOT NULL,
        email      TEXT NOT NULL,
        is_admin   INTEGER NOT NULL CHECK (is_admin IN (0,1))
    );
    """)

    # SOCIETIES TABLE:
    # each society has an auto-increment ID
    # society name must be unique (as requested)
    c.execute("""
    CREATE TABLE IF NOT EXISTS societies (
        societyID  INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL UNIQUE
    );
    """)

    # EVENTS TABLE:
    # eventID auto increments
    # event name must be unique
    # time_date is TEXT because assignment says it can be any string
    # fee is REAL, but if it is NULL we treat it as "Free"
    # owner stores which user created the event
    # ON DELETE CASCADE: if the user is deleted, their events are deleted too
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        eventID     INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL UNIQUE,
        time_date   TEXT NOT NULL,
        description TEXT NOT NULL,
        fee         REAL,              -- NULL means Free
        owner       TEXT NOT NULL,
        FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE
    );
    """)

    # EVENT_SOCIETIES TABLE (many-to-many):
    # one event can belong to multiple societies, and one society can have multiple events
    # composite primary key avoids duplicates (same event-society pair inserted twice)
    # ON DELETE CASCADE: if event or society is deleted, related rows here are deleted too
    c.execute("""
    CREATE TABLE IF NOT EXISTS event_societies (
        eventID    INTEGER NOT NULL,
        societyID  INTEGER NOT NULL,
        PRIMARY KEY(eventID, societyID),
        FOREIGN KEY(eventID) REFERENCES events(eventID) ON DELETE CASCADE,
        FOREIGN KEY(societyID) REFERENCES societies(societyID) ON DELETE CASCADE
    );
    """)

    # save changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # run this file directly to create the database tables
    createDatabase()
    print("Database ready:", DB_NAME)
