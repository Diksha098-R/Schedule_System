from pymongo import MongoClient

#Creating a pymongo client
client = MongoClient('localhost', 27017)

#Getting the database instance
db = client['Schedule_System']
print("Database created........" + str(db))

#Creating a collection
collection = db['Persons']
print("Collection created........" + str(collection))
collection_meetings = db['Meeting_Rooms']

#Inserting document into persons collection
doc1 = [{"_id":"Diksha2", "Meetings":[{"Date":"2021-02-03", "Start_Time":"2:30", "End_Time":"3:30", "Details":"Personal Meeting"}, {"Date":"2021-02-08", "Start_Time":"12:30", "End_Time":"13:00", "Details":"Customer Meeting"}]}, {"_id":"Pooja", "Meetings":[{"Date":"2021-02-06", "Start_Time":"9:30", "End_Time":"11:00", "Details":"Personal Meeting"}]}, {"_id":"Sayali", "Meetings":[{"Date":"2021-02-06", "Start_Time":"12:30", "End_Time":"13:00", "Details":"Team Meeting"}]}, {"_id":"Aboli", "Meetings":[{"Date":"2021-02-08", "Start_Time":"12:30", "End_Time":"14:00", "Details":"On site Meeting"}]}, {"_id":"Shivansh", "Meetings":[{"Date":"2021-02-09", "Start_Time":"14:00", "End_Time":"15:00", "Details":"Personal Meeting"}]}]
collection.insert_many(doc1)

doc2 = doc1 = [{"_id":"M100", "Meetings":[{"Date":"2021-02-04", "Start_Time":"2:30", "End_Time":"3:30"}, {"Date":"2021-02-09", "Start_Time":"12:30", "End_Time":"13:00"}]}, {"_id":"M101", "Meetings":[{"Date":"2021-02-07", "Start_Time":"8:30", "End_Time":"11:30"}]}, {"_id":"M102", "Meetings":[{"Date":"2021-02-08", "Start_Time":"13:30", "End_Time":"14:00"}]}, {"_id":"M103", "Meetings":[{"Date":"2021-02-08", "Start_Time":"16:00", "End_Time":"17:00"}]}]
collection_meetings.insert_many(doc2)
