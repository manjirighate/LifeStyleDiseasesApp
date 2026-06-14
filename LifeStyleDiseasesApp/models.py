import pymysql as mycon
import base64
import os  
from django.conf import settings  
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
import math
import re 
# Initialize once (important for performance)
sia = SentimentIntensityAnalyzer()
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text
def connect():
    try:
        con = mycon.connect(
            host='mysql-20e03ee7-lifestyle-5d79.i.aivencloud.com',
            user='avnadmin',
            password='AVNS_qQhEgU7ENEHbhtSTOh0',
            database='defaultdb',
            port=17795,
            ssl_disabled=False,   # Required for Aiven
            ssl_verify_cert=False # Disable verify if you don’t have certs
        )
        print(" MySQL connection established")
        return con
    except mycon.Error as e:
        print(" MySQL connection failed:", e)
        return None 
def getDoctors():
    conn = connect()
    #integrated security 
    cursor = conn.cursor() 
    cursor.execute('select * from doctors;')
    data=cursor.fetchall()
    conn.close()
    return data
def getUsers():
    conn = connect()
    #integrated security 
    cursor = conn.cursor() 
    cursor.execute('select userName,mobile,email,addr,profession,state,city from userdetails;')
    data=cursor.fetchall()
    conn.close()
    return data
def login(userid="NA", pass1="NA"):
    val = []
    conn = connect()
    cursor = conn.cursor()
    try:
        # Call the stored procedure directly
        cursor.callproc('userlogin', [userid, pass1])

        # Fetch all data returned by the stored procedure
        val = cursor.fetchall()
        print("Fetched:", val)

        conn.commit()
    except Exception as e:
        print("Error while executing stored procedure:", e)
    finally:
        cursor.close()
        conn.close()

    return val

def get_lat_long(pin, addr1):
    query = f"{addr1}, {pin}, India"
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "VehiclePartRecognition/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("Geo error:", e)

    return 0.0, 0.0
def insertUser(userid, password, username, address, mobile, email, gender, dob, state, city, profession,height,weight,pincode):
    """
    Inserts a new user using the MySQL stored procedure 'insertUser'.
    Updated parameter list as per the Django registration form.
    """
    conn = connect()
    cursor = conn.cursor()
    try:
        print(state)
        print()
        lat,lng=get_lat_long(pincode,(address+" ,"+city+", "+state))
        # Call your stored procedure with updated parameter order
        args = [userid, password, username, address, mobile, email, gender, dob, state, city, profession,height,weight,pincode,lat,lng]
        cursor.callproc('insertUser', args)

        conn.commit()
        print(" User inserted successfully via stored procedure")

    except Exception as e:
        print(" Error inserting user:", e)
        raise e

    finally:
        cursor.close()
        conn.close()

def updatePass(userid='NA',pass1='NA') : 
    val='NA'
    conn = connect()    
    cursor = conn.cursor()
    args = [userid,pass1]
    args1=cursor.callproc('updatePass', args)
    #print("Return value:", args1)
    #for result in cursor.stored_results():
       # val=result.fetchall()
        #print(result.fetchall())
    conn.commit()
    conn.close()
def insertDoctor(docname, speciality, photo, addr, education,
                 state, city, hospname, mobile,
                 opd_mor_timing,opd_eve_timing, opddays, fees,
                 userid, password,email,pincode,homevisit,homevisitcharges):

    conn = connect()
    cursor = conn.cursor()

    try:
        lat,lng=get_lat_long(pincode,(addr+" ,"+city+", "+state))
        args = [
            docname, speciality, photo, addr, education,
            state, city, hospname, mobile,
            opd_mor_timing,opd_eve_timing, opddays, fees,
            userid, password,email,pincode,lat,lng,homevisit,homevisitcharges
        ]

        cursor.callproc('insertDoctor', args)
        conn.commit()
        print(" Doctor inserted successfully")

    except Exception as e:
        print(" Error inserting doctor:", e)
        raise e

    finally:
        cursor.close()
        conn.close()
def getStates():
    try:
        print("in getstates")
        conn = connect()
        #integrated security 
        print("in getstates")
        cursor = conn.cursor() 
        cursor.execute('select state from statemaster;')
        data=cursor.fetchall()
        conn.close()
        return data
    except Exception as e:
        print("DB Error:", e)
def getCities(state="NA"):
    conn = connect()
    #integrated security 
    cursor = conn.cursor() 
    print("in cities")
    cursor.execute("select city from cities where state='"+state+"'")
    data=cursor.fetchall()
    conn.close()
    return data
def getDoctorDetails(userid="NA"):
    val=None
    conn = connect()    
    cursor = conn.cursor()
    try:
        query = "select speciality from doctors where userid = %s"  # Adjust table and column names as needed
        cursor.execute(query, (userid,))

        val = cursor.fetchall()  # Fetch all matching records
        print("Fetched Data:", val)

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        cursor.close()
        conn.close() 
    return val
def getUserDetails(userid="NA") : 
    val=None
    conn = connect()    
    cursor = conn.cursor()
    try:
        query = "SELECT *,TIMESTAMPDIFF(YEAR,STR_TO_DATE(dob, '%%Y-%%m-%%d'),CURDATE()) AS age,ROUND(weight / POWER(height / 100, 2), 2) AS bmi, CASE  WHEN LOWER(gender) = 'male' THEN 0   WHEN LOWER(gender) = 'female' THEN 1 ELSE NULL  END AS gender_numeric FROM userdetails WHERE userid = %s"  # Adjust table and column names as needed
        cursor.execute(query, (userid,))

        val = cursor.fetchall()  # Fetch all matching records
        print("Fetched Data:", val)

    except Exception as err:
        print("Error:", err)

    finally:
        cursor.close()
        conn.close() 
    return val
def getDiseases(userid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diseases where userid='"+userid.strip()+"'")
    data = cursor.fetchall()
    conn.close()
    return data
def getDiseasesUser(userid):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT diseaseName as disease FROM diseases WHERE userid=%s", (userid.strip(),))
    
    columns = [col[0] for col in cursor.description]  # get column names
    rows = cursor.fetchall()

    # Convert to list of dicts
    data = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return data
def insertDisease(userid, diseaseName, diseaseSts):
    conn = connect()
    cursor = conn.cursor()

    try:
        mxid = cursor.execute("SELECT IFNULL(MAX(did),1000) FROM diseases")
        cursor.execute("SELECT IFNULL(MAX(did),1000) FROM diseases")
        did = cursor.fetchone()[0] + 1

        cursor.execute(
            "INSERT INTO diseases VALUES (%s,%s,%s,%s)",
            (did, userid, diseaseName, diseaseSts)
        )

        conn.commit()

    except Exception as e:
        raise e

    finally:
        cursor.close()
        conn.close()
def insertLifestyle(userid, fruit, veg, fast, sugar, exercise,
                    sedentary, sleep, stress, smoke, alcohol, diab, heart,fiber_intake):

    conn = connect()
    cursor = conn.cursor()
    print("in lifestyle insert123")
    try:
        # keep one record per user
        cursor.execute("DELETE FROM lifestyle WHERE userid=%s", [userid])

        cursor.execute("""
            INSERT INTO lifestyle
            (userid, fruit_intake, vegetable_intake, fast_food_frequency,
             sugary_drinks_per_week, exercise_days_per_week,
             sedentary_hours_per_day, sleep_hours,
             stress_level, smoking_status, alcohol_consumption,
             family_history_diabetes, family_history_heart_disease,fiber_intake)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            userid, fruit, veg, fast, sugar, exercise,
            sedentary, sleep, stress, smoke, alcohol, diab, heart,fiber_intake
        ))

        conn.commit()

    except Exception as e:
        print("Lifestyle Insert Error:", e)
        raise e

    finally:
        cursor.close()
        conn.close()


# ---------------- REPORT ----------------
def getLifestyle1(userid):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fruit_intake, vegetable_intake, fast_food_frequency,
               sugary_drinks_per_week, exercise_days_per_week,
               sedentary_hours_per_day, sleep_hours,
               stress_level, smoking_status, alcohol_consumption,
               family_history_diabetes, family_history_heart_disease
        FROM lifestyle
        WHERE userid=%s
    """, [userid])

    data = cursor.fetchall()
    conn.close()
    return data
def getLifestyle(userid):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fruit_intake, vegetable_intake, fast_food_frequency,
               sugary_drinks_per_week, exercise_days_per_week,
               sedentary_hours_per_day, sleep_hours,
               stress_level, smoking_status, alcohol_consumption,
               family_history_diabetes, family_history_heart_disease,
               fiber_intake
        FROM lifestyle
        WHERE userid=%s
    """, [userid])

    rows = cursor.fetchall()
    conn.close()
    print("in model get lifestyle")
    print(rows)
     # ---------- Mapping Dictionaries ----------
    FRUIT_MAP = {
        0: "Very Low",
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Very High"
    }

    VEGETABLE_MAP = {
        0: "Almost None",
        1: "Small Amount",
        2: "Moderate Amount",
        3: "Good Amount",
        4: "A Lot"
    }

    FAST_FOOD_MAP = {
        0: "Almost Never",
        1: "Occasionally",
        2: "Few Times a Week",
        3: "Most Days",
        4: "Daily"
    }

    SUGAR_MAP = {
        0: "Very Low",
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Very High"
    }

    EXERCISE_MAP = {
        0: "None",
        1: "Less than 15 minutes",
        2: "15–30 minutes",
        3: "30–60 minutes",
        4: "More than 60 minutes"
    }
    STRESS_MAP = {
        0: "Low",
        1: "Moderate",
        2: "High",
        3: "Extreme"
    }
    FIBER_MAP = {
        0: "Very Little",
        1: "Little",
        2: "Moderate",
        3: "Good Amount",
        4: "A Lot"
    }
    SMOKING_MAP = {
    0: "Non-Smoker",
    1: "Smoker"
    }

    ALCOHOL_MAP = {
        0: "No",
        1: "Yes"
    }

    FAMILY_HISTORY_MAP = {
        0: "No",
        1: "Yes"
    }


    mapped_data = []
    """
    for r in rows:
        mapped_data.append([
            "fruit_intake": FRUIT_MAP.get(r[0], "N/A"),
            "vegetable_intake": VEGETABLE_MAP.get(r[1], "N/A"),
            "fast_food": FAST_FOOD_MAP.get(r[2], "N/A"),
            "sugary_drinks": SUGAR_MAP.get(r[3], "N/A"),
            "exercise": EXERCISE_MAP.get(r[4], "N/A"),
            "sedentary_hours": f"{r[5]} hrs/day",
            "sleep_hours": f"{r[6]} hrs/day",
            "stress_level": STRESS_MAP.get(r[7], "N/A"),
            "smoking_status": SMOKING_MAP.get(r[8], "N/A"),
            "alcohol_consumption": ALCOHOL_MAP.get(r[9], "N/A"),
            "family_history_diabetes": FAMILY_HISTORY_MAP.get(r[10], "N/A"),
            "family_history_heart_disease": FAMILY_HISTORY_MAP.get(r[11], "N/A"),
            "fiber_intake": FIBER_MAP.get(r[12], "N/A")
        ])
    """
    for r in rows:
        mapped_data.append([
            FRUIT_MAP.get(r[0], "N/A"),
            VEGETABLE_MAP.get(r[1], "N/A"),
            FAST_FOOD_MAP.get(r[2], "N/A"),
            SUGAR_MAP.get(r[3], "N/A"),
            EXERCISE_MAP.get(r[4], "N/A"),
            f"{r[5]} hrs/day",      # Sitting hours
            f"{r[6]} hrs/day",      # Sleep hours
            STRESS_MAP.get(int(r[7]), "N/A"),                  # Stress (already text)
            SMOKING_MAP.get(r[8], "N/A"),                  # Smoking
            ALCOHOL_MAP.get(r[9], "N/A"),                  # Alcohol
            FAMILY_HISTORY_MAP.get(r[10], "N/A"),                 # Family diabetes
            FAMILY_HISTORY_MAP.get(r[11], "N/A"),                  # Family heart disease
            FIBER_MAP.get(r[12], "N/A")
        ])
    print(mapped_data)
    return mapped_data

def getLifestyleold(userid):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fruit_intake, vegetable_intake, fast_food_frequency,
               sugary_drinks_per_week, exercise_days_per_week,
               sedentary_hours_per_day, sleep_hours,
               stress_level, smoking_status, alcohol_consumption,
               family_history_diabetes, family_history_heart_disease,fiber_intake
        FROM lifestyle
        WHERE userid=%s
    """, [userid])

    rows = cursor.fetchall()
    conn.close()

    # ---------- Mapping Dictionaries ----------
    FRUIT_MAP = {
        0: "Very Low",
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Very High"
    }

    VEGETABLE_MAP = {
        0: "Almost None",
        1: "Small Amount",
        2: "Moderate Amount",
        3: "Good Amount",
        4: "A Lot"
    }

    FAST_FOOD_MAP = {
        0: "Almost Never",
        1: "Occasionally",
        2: "Few Times a Week",
        3: "Most Days",
        4: "Daily"
    }

    SUGAR_MAP = {
        0: "Very Low",
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Very High"
    }

    EXERCISE_MAP = {
        0: "None",
        1: "Less than 15 minutes",
        2: "15–30 minutes",
        3: "30–60 minutes",
        4: "More than 60 minutes"
    }
    STRESS_MAP = {
        0: "Low",
        1: "Moderate",
        2: "High",
        3: "Extreme"
    }
    FIBER_MAP = {
        0: "Very Little",
        1: "Little",
        2: "Moderate",
        3: "Good Amount",
        4: "A Lot"
    }


    # ---------- Convert Numeric → Text ----------
    mapped_data = []
    
    for r in rows:
        mapped_data.append([
            FRUIT_MAP.get(r[0], "N/A"),
            VEGETABLE_MAP.get(r[1], "N/A"),
            FAST_FOOD_MAP.get(r[2], "N/A"),
            SUGAR_MAP.get(r[3], "N/A"),
            EXERCISE_MAP.get(r[4], "N/A"),
            f"{r[5]} hrs/day",      # Sitting hours
            f"{r[6]} hrs/day",      # Sleep hours
            STRESS_MAP.get(int(r[7].strip()), "N/A"),                  # Stress (already text)
            r[8],                  # Smoking
            r[9],                  # Alcohol
            r[10],                 # Family diabetes
            r[11],                  # Family heart disease
            FIBER_MAP.get(r[12], "N/A")
        ])
        print(r[7])

    return mapped_data

def checkLifestyleExists(userid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT lid FROM lifestyle WHERE userid=%s",
        (userid,)
    )
    data = cursor.fetchone()
    conn.close()
    return data
def getLifestyleByUser(userid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "select	fruit_intake,vegetable_intake,fiber_intake,sugary_drinks_per_week,fast_food_frequency,exercise_days_per_week,sedentary_hours_per_day,sleep_hours,stress_level,smoking_status,alcohol_consumption,family_history_diabetes ,family_history_heart_disease           FROM lifestyle WHERE userid=%s",(userid,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    columns = [
        "fruit_intake","vegetable_intake","fiber_intake",
        "sugar_intake","fast_food_intake",
        "exercise_minutes_per_day","sitting_hours_per_day",
        "sleep_hours","stress_level","smoking_status",
        "alcohol_consumption","family_history_diabetes",
        "family_history_heart_disease"
    ]

    return dict(zip(columns, row))
    return data
def checkChronicDiseaseExists(userid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cid FROM chronic_diseases WHERE userid=%s",
        (userid,)
    )
    data = cursor.fetchone()
    conn.close()
    return data

def checkChronicDiseaseExists(userid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT did FROM diseases WHERE userid=%s",
        (userid,)
    )
    data = cursor.fetchone()
    conn.close()
    return data
def searchSymptoms(q):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.symptom_name AS symptom,
               d.disease_name AS disease
        FROM symptoms s
        JOIN disease_symptom_map dm ON s.symptom_id = dm.symptom_id
        JOIN diseases_common d ON dm.disease_id = d.disease_id
        WHERE s.symptom_name LIKE %s
        LIMIT 10
    """, (q + "%",))
    rows = cur.fetchall()
    # convert tuple to dictionary
    data = []
    for r in rows:
        data.append({
            "symptom": r[0],
            "disease": r[1]
        })

    
    conn.close()
    return data
def extract_keywords(text):
    stopwords = {
        'is','am','are','was','were','the','a','an','and',
        'with','having','issue','problem','not','my','vehicle'
    }

    words = text.lower().split()
    return list(set(
        w for w in words if w not in stopwords and len(w) > 2
    ))

def findDoctorsBySpeciality(speciality, user_lat, user_lng):
    conn = connect()
    cursor = conn.cursor()

    query = """
    SELECT 
        d.docid,
        d.docname,
        d.speciality,
        d.city,
        d.hospname,
        d.fees,
        d.rating,
        d.photo,
        d.lat,
        d.lng,
        (
            6371 * ACOS(
                COS(RADIANS(%s)) * COS(RADIANS(d.lat)) *
                COS(RADIANS(d.lng) - RADIANS(%s)) +
                SIN(RADIANS(%s)) * SIN(RADIANS(d.lat))
            )
        ) AS distance,d.userid
    FROM doctors d
    WHERE d.speciality = %s
    ORDER BY distance ASC, d.rating DESC
    LIMIT 20
    """

    cursor.execute(query, [user_lat, user_lng, user_lat, speciality])
    return cursor.fetchall()
def findDoctorsNotBySpeciality(speciality, user_lat, user_lng, ids):
    conn = connect()
    cursor = conn.cursor()
    print("in not")
    query = """
    SELECT 
        d.docid,
        d.docname,
        d.speciality,
        d.city,
        d.hospname,
        d.fees,
        d.rating,
        d.photo,
        d.lat,
        d.lng,
        (
            6371 * ACOS(
                COS(RADIANS(%s)) * COS(RADIANS(d.lat)) *
                COS(RADIANS(d.lng) - RADIANS(%s)) +
                SIN(RADIANS(%s)) * SIN(RADIANS(d.lat))
            )
        ) AS distance,d.userid
    FROM doctors d
    WHERE d.speciality <> %s and d.speciality<>'Pediatrician' and d.userid in (select doctor_userid from doctor_disease_map where disease_id in ("""+ids+"""))
    ORDER BY distance ASC, d.rating DESC
    LIMIT 20
    """

    cursor.execute(query, [user_lat, user_lng, user_lat, speciality])
    print(query)
    return cursor.fetchall()
def findDiseasesBySymptoms(keywords):

    if not keywords:
        return []
    conn = connect()
    cursor = conn.cursor()

    conditions = " OR ".join(
        ["s.symptom_name LIKE %s"] * len(keywords)
    )

    query = f"""
    SELECT DISTINCT d.disease_id, d.disease_name,d.speciality
    FROM diseases_common d
    JOIN disease_symptom_map dm ON d.disease_id = dm.disease_id
    JOIN symptoms s ON dm.symptom_id = s.symptom_id
    WHERE {conditions}
    """

    params = [f"%{k}%" for k in keywords]

    cursor.execute(query, params)

    rows = cursor.fetchall()

    return [
        {"disease_id": r[0], "disease_name": r[1], "speciality": r[2]}
        for r in rows
    ]
def findDoctorsByDiseaseList(diseaseIds, user_lat, user_lng):

    if not diseaseIds:
        return []
    conn = connect()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(diseaseIds))

    query = f"""
    SELECT DISTINCT
        d.docid,
        d.docname,
        d.speciality,
        d.city,
        d.hospname,
        d.fees,
        d.rating,
        d.photo,
        d.lat,
        d.lng,
        (
            6371 * ACOS(
                COS(RADIANS(%s)) * COS(RADIANS(d.lat)) *
                COS(RADIANS(d.lng) - RADIANS(%s)) +
                SIN(RADIANS(%s)) * SIN(RADIANS(d.lat))
            )
        ) AS distance,d.userid
    FROM doctors d
    JOIN doctor_disease_map dd ON d.userid = dd.doctor_userid
    WHERE dd.disease_id IN ({placeholders})
    ORDER BY distance ASC, d.rating DESC
    LIMIT 20
    """

    params = [user_lat, user_lng, user_lat] + diseaseIds
    cursor.execute(query, params)

    return cursor.fetchall()
 
# ---------------------------
# ADD SYMPTOM
# ---------------------------
def addSymptom(symptom_name):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (%s)",
            (symptom_name,)
        )
        conn.commit()
        return True
    except Exception as e:
        print("Add symptom error:", e)
        return False
    finally:
        conn.close()


# ---------------------------
# GET ALL SYMPTOMS
# ---------------------------
def getAllSymptoms():
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT symptom_id, symptom_name FROM symptoms ORDER BY symptom_name"
    )
    data = cur.fetchall()
    conn.close()
    return data


# ---------------------------
# CHECK DUPLICATE
# ---------------------------
def symptomExists(symptom_name):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT symptom_id FROM symptoms WHERE symptom_name=%s",
        (symptom_name,)
    )
    row = cur.fetchone()
    conn.close()

    return row is not None

def getAllDiseases():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT disease_id, disease_name FROM diseases_common ORDER BY disease_name")
    data = cur.fetchall()
    conn.close()
    return data


def getAllSymptoms():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT symptom_id, symptom_name FROM symptoms ORDER BY symptom_name")
    data = cur.fetchall()
    conn.close()
    return data


def getDiseaseSymptomMap(spec):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.disease_name, s.symptom_name
        FROM disease_symptom_map m
        JOIN diseases_common d ON m.disease_id = d.disease_id
        JOIN symptoms s ON m.symptom_id = s.symptom_id where d.speciality='"""+spec+"""'
        ORDER BY d.disease_name
    """)
    data = cur.fetchall()
    conn.close()
    return data


def addDiseaseSymptomMapping(disease_id, symptom_ids):
    conn = connect()
    cur = conn.cursor()

    for sid in symptom_ids:
        cur.execute("""
            INSERT IGNORE INTO disease_symptom_map (disease_id, symptom_id)
            VALUES (%s, %s)
        """, [disease_id, sid])

    conn.commit()
    conn.close()
def getAllDoctors():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT userid, username
        FROM users
        WHERE utype='doctor'
        ORDER BY username
    """)
    data = cur.fetchall()
    conn.close()
    return data


def getAllDiseases():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT disease_id, disease_name
        FROM diseases_common
        ORDER BY disease_name
    """)
    data = cur.fetchall()
    conn.close()
    return data


def getDoctorDiseaseMap(docuid):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.did, d.disease_name
        FROM doctor_disease_map m
        JOIN users u ON m.doctor_userid = u.userid
        JOIN diseases_common d ON m.disease_id = d.disease_id and m.doctor_userid='"""+docuid+"""'
        ORDER BY m.did
    """)
    data = cur.fetchall()
    conn.close()
    return data


def addDoctorDiseaseMapping(doctor_userid, disease_ids):
    conn = connect()
    cur = conn.cursor()

    for did in disease_ids:
        cur.execute("""
            INSERT INTO doctor_disease_map (doctor_userid, disease_id)
            VALUES (%s, %s)
        """, [doctor_userid, did])

    conn.commit()
    conn.close()
def deleteDoctorDiseaseMapping(did):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM doctor_disease_map WHERE did=%s",
        [did]
    )
    conn.commit()
    conn.close()
def getCommonDiseases(spec):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT disease_id, disease_name, speciality
        FROM diseases_common where speciality='"""+spec+"""'
        ORDER BY disease_name
    """)
    data = cur.fetchall()
    conn.close()
    return data


def addCommonDisease(disease_name, speciality):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO diseases_common(disease_name, speciality)
        VALUES (%s, %s)
    """, [disease_name, speciality])
    conn.commit()
    conn.close()


def deleteCommonDisease(disease_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM diseases_common
        WHERE disease_id=%s
    """, [disease_id])
    conn.commit()
    conn.close()
def analyze_sentiment(review_text):
    """
    Returns:
        sentiment_label, sentiment_score
    """
    clean_text = preprocess_text(review_text)
    expanded_text = expand_with_wordnet(clean_text)

    score = sia.polarity_scores(expanded_text)
    compound = score["compound"]

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return sentiment, compound
def getDoctorDetails1(userid):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            docid,
            docname,
            speciality,
            education,
            hospname,
            mobile,
            addr,
            city,
            state,
            pincode,
            fees,
            opd_morning_timing,
            opd_eve_timing,
            opddays,
            homevisit,
            homecharges,
            rating,
            photo,
            lat,
            lng,
            userid
        FROM doctors
        WHERE userid = %s
    """, (userid,))

    data = cursor.fetchone()
    conn.close()
    return data
def getDoctorReviews(doctor_userid):
    conn = connect()
    cursor = conn.cursor()
     
    cursor.execute("""
        SELECT
            r.rating,
            r.review,
            u.userName,
            r.dt,
            r.sentiment,
            r.sentiment_score
        FROM doctor_reviews r
        JOIN userdetails u
            ON r.user_userid = u.userid
        WHERE r.doctor_userid = %s
        ORDER BY r.dt DESC
    """, (doctor_userid,))

    data = cursor.fetchall()
    conn.close()
    return data
def addDoctorReview(doctor_userid, user_userid, rating, review):
    conn = connect()
    cursor = conn.cursor()

    sentiment, score = analyze_sentiment(review)

    if not rating:
        rating = 1
    else:
        rating = int(rating)

    cursor.execute("""
        INSERT INTO doctor_reviews
        (doctor_userid, user_userid, rating, review, sentiment, sentiment_score)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        doctor_userid,
        user_userid,
        rating,
        review,
        sentiment,
        score
    ))

    conn.commit()
    conn.close()
def updateDoctorRating(doctor_userid):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE doctors
        SET rating = (
            SELECT ROUND(AVG(rating), 1)
            FROM doctor_reviews
            WHERE doctor_userid = %s
        )
        WHERE userid = %s
    """, (doctor_userid, doctor_userid))

    conn.commit()
    conn.close()
def expand_with_wordnet(text):
    words = text.split()
    expanded_words = []

    for word in words:
        expanded_words.append(word)
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                expanded_words.append(lemma.name().replace("_", " "))

    return " ".join(expanded_words)
