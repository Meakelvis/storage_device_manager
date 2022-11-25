from pyuac import main_requires_admin
import win32evtlog
import mysql.connector


# @main_requires_admin
def track():
    # connect to the db
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="transfer_monitor",
    )
    mycursor = mydb.cursor()

    while True:
        # connecting to events data
        h = win32evtlog.OpenEventLog("localhost", "Security")
        flags = (
            win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        )

        events = win32evtlog.ReadEventLog(h, flags, 0)

        extensions = [
            "mp4",
            "mov",
            "avi",
            "mkv",
            "wmv",
            "mpg",
            "vob",
            "avchd",
            "mp3",
            "wav",
        ]

        for event in events:
            if (event.EventID == 4662 or event.EventID == 4663) and (
                event.StringInserts[9] == "0x2" or event.StringInserts[7] == "Write"
            ):
                filename = event.StringInserts[6].split(".")

                recordid = event.RecordNumber
                mycursor.execute(
                    "SELECT * FROM files WHERE record_id = %s", (recordid,)
                )

                records = mycursor.fetchall()

                if records:
                    continue

                if filename[-1] in extensions:
                    # get event time
                    time = events[0].TimeGenerated

                    # store data in db
                    mycursor.execute(
                        "INSERT INTO files (record_id, name, extension, date, time) VALUES (%s, %s, %s, %s, %s)",
                        (
                            event.RecordNumber,
                            event.StringInserts[6],
                            filename[-1],
                            time.strftime("%Y-%m-%d"),
                            time.strftime("%H:%M:%S"),
                        ),
                    )

                    mydb.commit()
                else:
                    continue
            else:
                continue


if __name__ == "__main__":
    track()
