import calendar, re, json
from datetime import *

from flask import Flask, redirect, url_for, request, render_template
from pymongo import collection, MongoClient

app = Flask(__name__)

# Creating a pymongo client
client = MongoClient('localhost', 27017)

# Getting the database instance
db = client['Schedule_System']
print("Database created........" + str(db))

# Creating a collection
collection = db['Persons']
print("Collection created........" + str(collection))
collection_Meetings = db['Meeting_Rooms']
print("Meetings Collection created........" + str(collection_Meetings))

# global variables
extract_doc = {}
meeting_doc = {}
Date_time_len = ""
flag = 0
flag_persons = 0
meeting_room_error = 0
schedule_persons_error = 0
yy_mm = ""
yy = ""
mm = ""
dd = ""
cal_final = ""
dayNumber = ""
month = ""

# check for the calender to be displayed
def check_date(today):
    global yy_mm, yy, mm, dd, cal_final, dayNumber, month

    yy, mm, dd = today.split('-')
    yy_mm = str(yy) + str(mm)
    cal = calendar.TextCalendar(calendar.MONDAY)
    print_cal = cal.formatmonth(int(yy), int(mm))
    cal_split = re.split(' |\n', print_cal)
    cal_final = [x for x in cal_split if x != '']
    cal_final = cal_final[9:]
    if int(mm) < 8:
        dayNumber = calendar.weekday(int(yy), int(mm, 8), 0o1)
    else:
        dayNumber = calendar.weekday(int(yy), int(mm), 0o1)
    days =["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    month = calendar.month_name[int(mm)]

# get data from db
def extract_from_db(coll, find_query, find_condition):
    global Date_time_len
    send_doc = {}

    for doc in coll.find(find_query, find_condition):
        send_doc = doc

    Date_time = send_doc["Meetings"]
    Date_time_len = len(Date_time)

    return send_doc

# modify the data to be sent
def update_extract_doc(meeting_dt):
    global extract_doc
    send_doc = []
    meeting_dt = meeting_dt.split('-')

    for x in extract_doc["Meetings"]:
        chk_dt = x["Date"].split('-')

        if chk_dt[0] == meeting_dt[0] and chk_dt[1] ==  meeting_dt[1]:
            send_doc.append(x)
    extract_doc["Meetings"] = send_doc

# check for collisions in timings
def collision_check_timings(meeting_dt, meeting_st, meeting_et, meeting_dates, meeting_start_time, meeting_end_time):
    meeting_st_comp = datetime.strptime(meeting_st, '%H:%M').time()
    meeting_et_comp = datetime.strptime(meeting_et, '%H:%M').time()

    for i in range(len(meeting_dates)):
        if meeting_dates[i] == meeting_dt:
            time1 = datetime.strptime(meeting_start_time[i], '%H:%M').time()
            time2 = datetime.strptime(meeting_end_time[i], '%H:%M').time()
            if (time1 <= meeting_st_comp < time2) or (time1 < meeting_et_comp <= time2) or (meeting_st_comp <= time1 and meeting_et_comp >= time2):
                # send error
                return 1
    # if no error
    return 0


@app.route('/')
def on_start():
    global extract_doc
    today = datetime.today().strftime('%Y-%m-%d')
    check_date(today)
    find_query = {"_id": "Diksha2"}
    find_condition = {"Meetings": 1, "_id": 0}

    extract_doc = extract_from_db(collection, find_query, find_condition)
    update_extract_doc(today)
    return render_template("Schedule_System.html", error=0, yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len)

# schedule meeting for a single person
def schedule_meeting(meeting_dt, meeting_st, meeting_et, meeting_details):
    global meeting_doc, extract_doc, schedule_persons_error, flag_persons

    meeting_dates = []
    meeting_start_time = []
    meeting_end_time = []

    find_query = {"_id":"Diksha2"}
    find_condition = {"Meetings": 1, "_id": 0}
    meeting_doc = extract_from_db(collection, find_query, find_condition)

    for i in range(len(meeting_doc["Meetings"])):
        meeting_dates.append(meeting_doc["Meetings"][i]["Date"])
        meeting_start_time.append(meeting_doc["Meetings"][i]["Start_Time"])
        meeting_end_time.append(meeting_doc["Meetings"][i]["End_Time"])

    if collision_check_timings(meeting_dt, meeting_st, meeting_et, meeting_dates, meeting_start_time, meeting_end_time) == 1:
        # send error
        schedule_persons_error = 1
        extract_doc = extract_from_db(collection, find_query, find_condition)
        update_extract_doc(meeting_dt)
        return render_template("Schedule_System.html", error="1", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm="", per="")
    else:
        # inserting in db
        update_doc = {"$push": {"Meetings": {"$each": [{"Date": str(meeting_dt), "Start_Time": str(meeting_st), "End_Time": str(meeting_et), "Details": str(meeting_details)}], "$sort": {"Date": 1}}}}
        collection.update_one(find_query, update_doc)
    if flag_persons == 0:
        # check if called by book_meeting function
        extract_doc = extract_from_db(collection, find_query, find_condition)
        update_extract_doc(meeting_dt)
        return render_template("Schedule_System.html", error="0", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm="", per="")
    else:
        flag_persons = 0
        return 0

# book meeting room
def book_meeting_room(meeting_dt, meeting_st, meeting_et, meeting_room, meeting_details):
    global error, meeting_doc, extract_doc, flag, meeting_room_error, schedule_persons_error, flag_persons

    meeting_dates = []
    meeting_start_time = []
    meeting_end_time = []

    meeting_query = {"_id": str(meeting_room)}
    meeting_find_condition = {"Meetings": 1, "_id": 0}
    find_query = {"_id": "Diksha2"}
    meeting_update_doc = {"$push": {"Meetings": {"$each": [{"Date": str(meeting_dt), "Start_Time": str(meeting_st), "End_Time": str(meeting_et)}], "$sort": {"Date": 1}}}}

    meeting_doc = extract_from_db(collection_Meetings, meeting_query, meeting_find_condition)

    for i in range(len(meeting_doc["Meetings"])):
        meeting_dates.append(meeting_doc["Meetings"][i]["Date"])
        meeting_start_time.append(meeting_doc["Meetings"][i]["Start_Time"])
        meeting_end_time.append(meeting_doc["Meetings"][i]["End_Time"])

    if collision_check_timings(meeting_dt, meeting_st, meeting_et, meeting_dates, meeting_start_time, meeting_end_time) == 1:
        # send error
        meeting_room_error = 1

        extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
        update_extract_doc(meeting_dt)
        return render_template("Schedule_System.html", error="2", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm="", per="")

    if flag == 0:
        # check if calling schedule meeting function?
        flag_persons = 1
        schedule_meeting(meeting_dt, meeting_st, meeting_et, meeting_details)
        if schedule_persons_error == 1:
            schedule_persons_error = 0
            extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
            update_extract_doc(meeting_dt)
            return render_template("Schedule_System.html", error="1", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per="")

    # update db
    collection_Meetings.update_one(meeting_query, meeting_update_doc)

    if flag == 0:
        extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
        update_extract_doc(meeting_dt)

        return render_template("Schedule_System.html", error="0", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per="")
    else:
        flag = 0
        return 0


def participant_meeting(meeting_dt, meeting_st, meeting_et, meeting_details, meeting_room, participants_original, checked_room):
    global extract_doc, meeting_doc, flag, meeting_room_error
    all_meetings = []
    all_ids = []
    meeting_dates = []
    meeting_start_time = []
    meeting_end_time = []

    participants = participants_original.split(',')
    participants.append("Diksha2")
    for doc in collection.find():
        all_meetings.append(doc)
        all_ids.append(doc["_id"])

    find_query = {"_id": "Diksha2"}
    meeting_find_condition = {"Meetings": 1, "_id": 0}

    for participant_id in all_ids:
        if participant_id in participants:
            index1 = all_ids.index(participant_id)
            for i in range(len(all_meetings[index1]["Meetings"])):
                meeting_dates.append(all_meetings[index1]["Meetings"][i]["Date"])
                meeting_start_time.append(all_meetings[index1]["Meetings"][i]["Start_Time"])
                meeting_end_time.append(all_meetings[index1]["Meetings"][i]["End_Time"])

            if collision_check_timings(meeting_dt, meeting_st, meeting_et, meeting_dates, meeting_start_time, meeting_end_time) == 1:
                # send error
                extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
                update_extract_doc(meeting_dt)
                return render_template("Schedule_System.html", error="3", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm="", per="")

    # check collision with meeting room ----------------------------------------------------------
    if checked_room == "on":
        flag = 1
        book_meeting_room(meeting_dt, meeting_st, meeting_et, meeting_room, meeting_details)
        if meeting_room_error == 1:
            meeting_room_error = 0
            extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
            update_extract_doc(meeting_dt)
            return render_template("Schedule_System.html", error="2", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per=participants_original)

    # update example collection in db -------------------------------------------------------
    update_participant_doc = {"$push": {"Meetings": {"$each": [{"Date": str(meeting_dt), "Start_Time": str(meeting_st), "End_Time": str(meeting_et), "Details": str(meeting_details)}], "$sort": {"Date": 1}}}}

    for part in participants:
        query_participant = {"_id": str(part)}
        collection.update_one(query_participant, update_participant_doc)

    extract_doc = extract_from_db(collection, find_query, meeting_find_condition)
    update_extract_doc(meeting_dt)

    return render_template("Schedule_System.html", error="0", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per=participants_original)


@app.route('/book_meeting', methods = ['POST', 'GET'])
def book_meeting():
    global meeting_doc, extract_doc
    meeting_room = ""
    participants_original = ""

    meeting_dt = request.form['date']
    meeting_st = request.form['start_time']
    meeting_et = request.form['end_time']
    meeting_details = request.form['meeting_details']

    time1 = datetime.strptime(meeting_st, '%H:%M').time()
    time2 = datetime.strptime(meeting_et, '%H:%M').time()
    today = datetime.today().strftime('%Y-%m-%d')
    today = today.split('-')
    chk_dt = meeting_dt.split('-')
    chk_today = datetime(int(today[0]), int(today[1]), int(today[2]))
    chk_dt = datetime(int(chk_dt[0]), int(chk_dt[1]), int(chk_dt[2]))
    if time1 >= time2:
        return render_template("Schedule_System.html", error="4", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per=participants_original)
    if chk_dt < chk_today:
        return render_template("Schedule_System.html", error="5", yy_mm=yy_mm, yy=yy, month=month, dd=dd, dayNumber=dayNumber, last_date=int(cal_final[-1]), Date_time=extract_doc, Date_time_len=Date_time_len, dt=meeting_dt, st=meeting_st, et=meeting_et, rm=meeting_room, per=participants_original)

    check_cal = meeting_dt.split('-')
    if check_cal[0] != yy or check_cal[1] != mm:
        check_date(meeting_dt)

    checked_room = request.form.get('meeting_rooms_checkbox')   # result is on/None
    checked_participants = request.form.get('meeting_people')   # result is on/None

    if checked_room == None and checked_participants == None:
        return schedule_meeting(meeting_dt, meeting_st, meeting_et, meeting_details)
    elif checked_room == "on" and checked_participants == None:
        meeting_room = request.form['meeting_rooms']
        meeting_details = meeting_details + " - " + meeting_room
        return book_meeting_room(meeting_dt, meeting_st, meeting_et, meeting_room, meeting_details)
    elif checked_participants == "on":
        participants_original = request.form['participant_textbox']
        meeting_room = request.form['meeting_rooms']
        meeting_details = meeting_details + " - " + participants_original + " - " + meeting_room
        return participant_meeting(meeting_dt, meeting_st, meeting_et, meeting_details, meeting_room, participants_original, checked_room)

if __name__ == '__main__':
   app.run(debug = True)
