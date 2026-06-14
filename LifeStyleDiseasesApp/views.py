from django.http import HttpResponse
from  django.shortcuts import render
from . import models
from django.core.files.storage import FileSystemStorage
import random
import mysql.connector as mycon
from datetime import date
from datetime import datetime
from django.utils.timezone import now
import ast
from django import template
from django.http import JsonResponse
from .ml_utils import predict_diseases
from django.shortcuts import render, redirect
import os
import pandas as pd
from django.conf import settings
def index(request):
    data= models.getStates()
    return render(request, "index.html",{"list":data})
def load_recommendation_data():
    base_path = os.path.join(settings.BASE_DIR, "static/recommendations")

    health_df = pd.read_csv(os.path.join(base_path, "health_recommendations_detailed.csv"))
    yoga_df = pd.read_csv(os.path.join(base_path, "yoga_recommendations.csv"))
    diet_df = pd.read_csv(os.path.join(base_path, "diet_plans.csv"))

    #   CLEAN COLUMN NAMES (CRITICAL FIX)
    for df in [health_df, yoga_df, diet_df]:
        df.columns = df.columns.str.strip().str.lower()

    #  DEBUG PRINT (run once)
    print("COLUMNS AFTER CLEANING:", health_df.columns.tolist())

    return health_df, yoga_df, diet_df
def generate_full_recommendations(predictions, existing_diseases):
    health_df, yoga_df, diet_df = load_recommendation_data()

    final = {
        "Diet": [],
        "Exercise": [],
        "Preventive": [],
        "Suggestion": [],
        "Yoga": [],
        "MealPlan": []
    }

    for disease, data in predictions.items():

        disease_name = disease.replace("_risk", "")

        #  Check if already exists
        if disease_name in existing_diseases:
            level = "Already Exists"
        else:
            level = data["level"]

        # ---------------- HEALTH RECOMMENDATIONS ----------------
        filtered = health_df[
            (health_df["disease"].isin([disease_name, "general"])) &
            (health_df["risk_level"] == level)
        ]

        for _, row in filtered.iterrows():
            final[row["category"]].append({
                "title": row["title"],
                "description": row["description"]
            })

        # ---------------- YOGA ----------------
        yoga_filtered = yoga_df[
            (yoga_df["disease"].isin([disease_name, "general"])) &
            (yoga_df["risk_level"] == level)
        ]

        for _, row in yoga_filtered.iterrows():
            final["Yoga"].append({
                "title": row["pose_name"],
                "description": f"{row['description']} ({row['duration']})"
            })

        # ---------------- DIET ----------------
        diet_filtered = diet_df[
            (diet_df["disease"].isin([disease_name, "general"])) &
            (diet_df["risk_level"] == level)
        ]

        for _, row in diet_filtered.iterrows():
            final["MealPlan"].append({
                "title": row["meal_type"],
                "description": row["meal_plan"]
            })

    # ✅ Remove duplicates
    for key in final:
        final[key] = [dict(t) for t in {tuple(d.items()) for d in final[key]}]

    return final
def searchSymptoms(request):
    q = request.GET.get("q", "")
    data = models.searchSymptoms(q)
    print(data)
    return JsonResponse(data, safe=False)

def registerDoctor(request):
    if request.method == 'POST':

        docname     = request.POST.get("docname")
        speciality  = request.POST.get("speciality")
        mobile      = request.POST.get("mobile")
        education   = request.POST.get("education")
        hospname    = request.POST.get("hospname")
        state       = request.POST.get("state")
        city        = request.POST.get("cities")
        opddays     = request.POST.get("opd_day_from")+"-"+request.POST.get("opd_day_to")
        opd_mor_timing  = request.POST.get("morning_hour")+":"+request.POST.get("morning_minute")+" "+request.POST.get("morning_ampm")
        opd_eve_timing  = request.POST.get("eve_hour")+":"+request.POST.get("eve_minute")+" "+request.POST.get("eve_ampm")
         
        fees        = request.POST.get("fees")
        addr        = request.POST.get("addr")
        userid      = request.POST.get("userid")
        password    = request.POST.get("password")
        email    = request.POST.get("email")
        pincode    = request.POST.get("pincode")
        homevisit1    = request.POST.get("home_visit")
        homevisitcharges1    =0
        if homevisit1=="yes":
            homevisitcharges1= request.POST.get("home_visit_charges")
        # ---------- PHOTO UPLOAD ----------
        photo_path = ""
        if request.FILES.get("photo"):
            photo = request.FILES["photo"]
            fs = FileSystemStorage(location="static/doctors/")
            filename = fs.save(photo.name, photo)
            photo_path = "doctors/" + filename

        try:
            models.insertDoctor(
                docname=docname,
                speciality=speciality,
                photo=photo_path,
                addr=addr,
                education=education,
                state=state,
                city=city,
                hospname=hospname,
                mobile=mobile,
                opd_mor_timing=opd_mor_timing,
                opd_eve_timing=opd_eve_timing,
                opddays=opddays,
                fees=fees,
                userid=userid,
                password=password,
                email=email,
                pincode=pincode,
                homevisit=homevisit1,
                homevisitcharges=homevisitcharges1 )

            return JsonResponse({"message": "Doctor registered successfully!"})

        except Exception as e:
            print("Doctor registration error:", e)
            return JsonResponse({"message": "Doctor registration failed!"})
def registeruser(request):
    if request.method == 'POST':
        userid = request.POST.get("userid")
        usernm = request.POST.get("name")
        pswd = request.POST.get("pass")
        emailid = request.POST.get("email")
        mobileno = request.POST.get("mobile")
        gender1 = request.POST.get("gender")
        addr = request.POST.get("addr")
        height1 = request.POST.get("height")
        weight1 = request.POST.get("weight")
        state = request.POST.get("state")
        city = request.POST.get("cities")  # may be dynamically loaded
        dob1 = request.POST.get("dob")
        pincode = request.POST.get("pincode")  # profession field

        print("UserID:", userid)
        print("Username:", usernm)
        print("Password:", pswd)
        print("Email:", emailid)
        print("Mobile:", mobileno)
        #print("Gender:", gender)
        print("Address:", addr)
        #print("State:", state)
        #print("City:", cities)
        #print("DOB:", dob)
        #print("Profession:", prof)

        try:
            # Call your custom insert function (adapt parameters as needed)
            models.insertUser(
                userid=userid,
                password=pswd,
                username=usernm,
                address=addr,
                mobile=mobileno,
                email=emailid,
                gender=gender1,
                dob=dob1,
                state=state,
                city=city,
                profession="NA",
                height=height1,
                weight=weight1,
                pincode=pincode,
            
            )

            return JsonResponse({
            "message": "Registration successful!"})

        except Exception as e:
            print("Registration error:", e)
            return JsonResponse({"message": "Registration Failed!"})
def viewDoctors(request):
    data= models.getDoctors()
    data1=models.getStates()
    #dash=models.getAdminDash() 
    return render(request, "doctors.html",{"list":data,"states":data1})  
def get_age_range(age):
    if age < 2:
        return "infant"
    elif age < 12:
        return "child"
    elif age < 18:
        return "teen"
    elif age < 60:
        return "adult"
    else:
        return "senior"
def is_long_duration(duration_value,duration_unit):
    print("duration value")
    print(duration_value)
    print(duration_unit)
       # Normalize to days
    if duration_unit == "days":
        total_days = duration_value

    elif duration_unit == "weeks":
        total_days = duration_value * 7

    elif duration_unit == "months":
        total_days = duration_value * 30   # approx month

    else:
        return False  # unknown unit
    print("total days")
    print(total_days)
    return total_days >= 14   # 2 weeks threshold

def recommendDoctors(request):

    symptoms = request.GET.get("symptoms", "").strip()
    speciality = request.GET.get("speciality", "").strip()
    locationType = request.GET.get("locationType")
    patientType = request.GET.get("patientType")   # self / other
    duration_days = int(request.GET.get("durationValue", "0"))
    duration_unit= request.GET.get("durationUnit")
    age_range = request.GET.get("ageRange")
    forced_speciality = None

    # --------------------------------
    # 0️⃣ AGE RESOLUTION
    # --------------------------------
    if patientType == "self":
        age = request.session.get("age")

        if age:
            age_range = get_age_range(age)

    # --------------------------------
    # 1️⃣ AGE-BASED SPECIALITY LOGIC
    # --------------------------------
    if age_range in ["infant", "child"]:
        forced_speciality = "Pediatrician"

    elif age_range == "teen":
        forced_speciality = speciality if speciality else "General Physician"

    elif age_range == "senior":
        forced_speciality = speciality  # boost later via ranking

    # --------------------------------
    # 2️⃣ RESOLVE USER LOCATION
    # --------------------------------
    if locationType == "other":
        state = request.GET.get("state")
        city = request.GET.get("city")
        address = request.GET.get("address")
        pincode = request.GET.get("pincode")

        full_address = f"{address}, {city}, {state}"

        try:
            user_lat, user_lng = models.get_lat_long(pincode, full_address)
        except Exception:
            return render(request, "findDoctors.html", {
                "list": [], "error": "Unable to locate given address"
            })
    else:
        user_lat = request.session.get("lat")
        user_lng = request.session.get("lng")

        if not user_lat or not user_lng:
            return render(request, "findDoctors.html", {
                "list": [], "error": "User location not available"
            })

    # --------------------------------
    # 3️⃣ DOCTOR RECOMMENDATION LOGIC
    # --------------------------------

    # CASE 1️⃣ Age-forced speciality
    if forced_speciality:
        doctors = models.findDoctorsBySpeciality(
            forced_speciality, user_lat, user_lng
        )

    # CASE 2️⃣ Explicit speciality chosen
    elif speciality:
        doctors = models.findDoctorsBySpeciality(
            speciality, user_lat, user_lng
        )

    # CASE 3️⃣ Symptoms-based intelligent routing
    elif symptoms:
        keywords = models.extract_keywords(symptoms)

        diseases = models.findDiseasesBySymptoms(keywords)
        print("diseases")
        print(diseases)
        disease_ids = [d["disease_id"] for d in diseases]
        disease_specialities = set(d["speciality"] for d in diseases)

        # 👨‍⚕️ Adult intelligent routing
        if age_range == "adult":
            print("adult")
            print(disease_specialities)    
            # If GP + Specialist both possible
            if "General Physician" in disease_specialities and len(disease_specialities) > 1:

                if is_long_duration(duration_days,duration_unit):
                    # long duration → specialist
                    disease_id1=""
                    for d in diseases:
                        if disease_id1=="":
                            disease_id1=str(d["disease_id"])
                        else:
                            disease_id1+=","+str(d["disease_id"])
                    print(disease_id1)
                    disease_ids = [
                        d["disease_id"] for d in diseases
                    #    if d["speciality"] != "General Physician"
                    ]
                    doctors = models.findDoctorsNotBySpeciality(
                        "General Physician", user_lat, user_lng,disease_id1
                    )
                    return render(request, "findDoctors.html", {
                        "list": doctors,
                        "user_lat": user_lat,
                        "user_lng": user_lng,
                        "age_range": age_range
                    })

                else:
                    # short duration → GP
                    print("in else short duration")
                    doctors = models.findDoctorsBySpeciality(
                        "General Physician", user_lat, user_lng
                    )
                    print("doctors")
                    print(doctors)
                    return render(request, "findDoctors.html", {
                        "list": doctors,
                        "user_lat": user_lat,
                        "user_lng": user_lng,
                        "age_range": age_range
                    })

        # Normal disease-based mapping
        if disease_ids:
            doctors = models.findDoctorsByDiseaseList(
                disease_ids, user_lat, user_lng
            )
        else:
            doctors = []

    else:
        doctors = []
    
    # --------------------------------
    # 4️⃣ RENDER RESULT
    # --------------------------------
    return render(
        request,
        "findDoctors.html",
        {
            "list": doctors,
            "user_lat": user_lat,
            "user_lng": user_lng,
            "age_range": age_range
        }
    )


def recommendDoctors2(request):

    symptoms = request.GET.get("symptoms")
    speciality = request.GET.get("speciality")
    locationType = request.GET.get("locationType")
    age_range = request.GET.get("ageRange")

    if age_range in ["infant", "child"]:
        forced_speciality = "Pediatrician"

    elif age_range == "teen":
        forced_speciality = speciality or "General Physician"

    elif age_range == "senior":
        forced_speciality = speciality  # but boost senior priority
    # --------------------------------
    # 1️⃣ RESOLVE USER LOCATION
    # --------------------------------
    if locationType == "other":
        state = request.GET.get("state")
        city = request.GET.get("city")
        address = request.GET.get("address")
        pincode = request.GET.get("pincode")

        full_address = f"{address}, {city}, {state}"

        try:
            user_lat, user_lng = models.get_lat_long(pincode, full_address)
        except Exception:
            return render(
                request,
                "findDoctors.html",
                {
                    "list": [],
                    "error": "Unable to locate given address"
                }
            )
    else:
        # use registered address
        user_lat = request.session.get("lat")
        user_lng = request.session.get("lng")
        print(user_lat)
        print(user_lng)
        if not user_lat or not user_lng:
            return render(
                request,
                "findDoctors.html",
                {
                    "list": [],
                    "error": "User location not available"
                }
            )

    # --------------------------------
    # 2️⃣ FIND DOCTORS
    # --------------------------------

    # CASE 1: Speciality directly selected
    if speciality:
        doctors = models.findDoctorsBySpeciality(
            speciality, user_lat, user_lng
        )

    # CASE 2: Symptoms based search
    else:
        if not symptoms:
            doctors = []
        else:
            keywords = models.extract_keywords(symptoms)
            print(keywords)
            diseases = models.findDiseasesBySymptoms(keywords)
            diseaseIds = [d["disease_id"] for d in diseases]

            if diseaseIds:
                doctors = models.findDoctorsByDiseaseList(
                    diseaseIds, user_lat, user_lng
                )
            else:
                doctors = []

    # --------------------------------
    # 3️⃣ RENDER PARTIAL RESULT
    # --------------------------------
    return render(
        request,
        "findDoctors.html",
        {
            "list": doctors,
            "user_lat": user_lat,
            "user_lng": user_lng
        }
    )
def recommendDoctors1(request):
    symptoms = request.GET.get("symptoms")
    speciality = request.GET.get("speciality")
    locationType = request.GET.get("locationType")
    # -----------------------------
    # 1️⃣ RESOLVE USER LOCATION
    # -----------------------------
    if locationType == "other":
        state = request.GET.get("state")
        city = request.GET.get("city")
        address = request.GET.get("address")
        pincode = request.GET.get("pincode")

        full_address = f"{address}, {city}, {state}"

        try:
            user_lat, user_lng = models.get_lat_long(pincode, full_address)
        except Exception:
            data2= models.getStates()
            userid = request.session["userid"]
            data= models.getUserDetails(userid)
            return render(
                request,
                "search_doctor.html",
                {"list":data,"states":data2, "error": "Unable to locate address"}
            )
    else:
        # Default → registered address
        user_lat = request.session["lat"]
        user_lng = request.session["lng"]

        if not user_lat or not user_lng:
            data2= models.getStates()
            userid = request.session["userid"]
            data= models.getUserDetails(userid)
            return render(
                request,
                "search_doctor.html",
                {"list":data,"states":data2, "error": "User location not available"}
            ) 
    # 1. Detect disease / speciality
    # 2. Fetch matching doctors
    # 3. Sort by distance + rating + reviews
    # 4. Return HTML fragment

    doctors = models.getRecommendedDoctors(...)
    return render(request,"doctor_results.html",{"doctors":doctors})

def admin(request): 
    data= models.getUsers()
    #dash=models.getAdminDash() 
    return render(request, "admin.html",{"list":data}) 
def analyze_lifestyle1(request):
    return render(request, "analyze_lifestyle.html",{"list":data}) 
def doctor(request): 
    data= models.getUsers()
    #dash=models.getAdminDash() 
    userid = request.session["userid"]
    details=models.getDoctorDetails(userid)
    request.session["speciality"]=details[0][0] 
    return render(request, "doctor.html",{"list":data}) 
def user(request): 
    #data2= models.getStates()
    userid = request.session["userid"]
    data= models.getUserDetails(userid)
    print("lat and lng")
    print(data)
    print(data[0][15])
    print(data[0][16])
    request.session["lat"]=data[0][15]
    request.session["lng"]=data[0][16]
    request.session["age"]=data[0][17]
    request.session["bmi"]=data[0][18]
    request.session["gender"]=data[0][19]
    #dash=models.getAdminDash() 
    return render(request, "user.html") 

def search_doctors(request): 
    data2= models.getStates()
    userid = request.session["userid"]
    data= models.getUserDetails(userid)
    #dash=models.getAdminDash() 
    return render(request, "search_doctor.html",{"list":data,"states":data2}) 
def logout(request):
    data= models.getStates()
    try:
        del request.session["user"]          
    except:
        print("")
    today_minus_10 = date.today().replace(year=date.today().year - 10).isoformat() 
    return render(request, "index.html",{"list":data,"today_minus_10":today_minus_10})
def changePass(request):
    if request.method == 'POST':
        userid=request.POST.get("userid")  
        pass1=request.POST.get("pass").strip()  
        oldpass=request.POST.get("oldpass").strip()  
        val=models.checkpass(userid,oldpass)
        if(len(val)>0):
            models.updatePass(userid,pass1) 
            return render(request, "Success1.html",{"mess":"Password Changed Successfully..!!","link":"/user"})
        else:        
            return render(request, "Success1.html",{"mess":"Authentication Failed!! Try again!!","link":"/user"})
def changePassReg(request):
    return render(request, "ChangePass.html")
  
def logout(request):
    #data= models.getStates()
    try:
        del request.session["user"]          
    except:
        print("")
    return render(request, "index.html" )
   
 
def login(request):
    if request.method == 'POST':
        userid=request.POST.get("userid") 
        pass1=request.POST.get("pass") 
        val=models.login(userid,pass1)
        if(len(val)>0): 
            request.session["user"]={"userid":val[0][0],"utype":val[0][4],"username":val[0][2]}    
            request.session["userid"]=val[0][0] 
            request.session["username"]=val[0][1]
            request.session["emailid"]=val[0][5]  
            if val[0][4]=="admin": 
                #dash=models.getAdminDash() 
                redirect_url="/admin/"             
            elif val[0][4]=="user":
                details=models.getUserDetails(userid)
                #request.session["photo"]=details[0][10] 
                #dash=models.getUserDash(userid)
               # data= models.getPredictionsHistory(userid)
                 
                redirect_url="/user/"
            elif val[0][4]=="doctor":
                details=models.getDoctorDetails(userid)
                request.session["speciality"]=details[0][0] 
                #dash=models.getUserDash(userid)
               # data= models.getPredictionsHistory(userid) 
                redirect_url="/doctor/"
                      
            
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Authentication Failed!"
                })

            return JsonResponse({
                "status": "success",
                "redirect": redirect_url
            })

        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid User ID or Password"
            }) 
         
def Cities(request):
    data= models.getCities(request.GET.get("state"))    
    print(data)
    return render(request, "cities.html",{"list":data})
def registerDisease(request):
    if request.method == "POST":
        userid = request.session['userid'] 
        diseaseName = request.POST.get("diseaseName")
        diseaseSts = request.POST.get("diseaseSts")
        print(diseaseName)
        try:
            models.insertDisease(userid, diseaseName, diseaseSts)
            return JsonResponse({"message": "Disease registered successfully!"})

        except Exception as e:
            print("Disease insert error:", e)
            return JsonResponse({"message": "Disease registration failed!"})
def viewDiseases(request):
    userid = request.session['userid'] 
    data = models.getDiseases(userid)
    return render(request, "diseases.html", {"list": data})
def lifestyle(request):
    userid = request.session['userid'] 

    # ---------- INSERT ----------
    if request.method == "POST":
        try:
            print("in lifestyle insert")
            models.insertLifestyle(
                userid=userid,
                fruit=request.POST.get("fruit_intake"),
                veg=request.POST.get("vegetable_intake"),
                fast=request.POST.get("fast_food_frequency"),
                sugar=request.POST.get("sugary_drinks_per_week"),
                exercise=request.POST.get("exercise_days_per_week"),
                sedentary=request.POST.get("sedentary_hours_per_day"),
                sleep=request.POST.get("sleep_hours"),
                stress=request.POST.get("stress_level"),
                smoke=request.POST.get("smoking_status"),
                alcohol=request.POST.get("alcohol_consumption"),
                diab=request.POST.get("family_history_diabetes"),
                heart=request.POST.get("family_history_heart_disease"),
                fiber_intake=request.POST.get("fiber_intake")
            )
            print("in lifestyle insert11")
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error"})

    # ---------- REPORT ----------
    data = models.getLifestyle(userid)
    print("====================#########")
    print(data)
    return render(request, "lifestyle.html", {"list": data})
def get_factor_level(value, low, high):
    if value <= low:
        return "Low"
    elif value <= high:
        return "Moderate"
    return "High"


def analyze_lifestyle(request):
    userid = request.session.get("userid")

    if not userid:
        return redirect("/login/")

    # Check lifestyle data
    if not models.checkLifestyleExists(userid):
        return redirect("/lifestyle/")

    lifestyle_data = models.getLifestyleByUser(userid)
    if not lifestyle_data:
        return redirect("/lifestyle/")

    # ---- FETCH FROM SESSION ----
    age = request.session.get("age")
    bmi = request.session.get("bmi")
    gender = request.session.get("gender")  # male=0, female=1

    # ---- COMBINE FEATURES ----
    features = {
        "age": age,
        "gender": gender,
        "bmi": bmi,
        **lifestyle_data
        
    }
    print("ggggggggggggggggggggggggggggg")
    print(features["age"])
    print("=========================")
    print(features)
    # ---- ML PREDICTION ----
    ml_result = predict_diseases(features)
    print("^^^^^^^^^^^^^^^")
    print(lifestyle_data)
    print("ML result")
    print(ml_result)
    high_risks = [
        disease for disease, data in ml_result.items()
        if data["level"] in ["Moderate", "High"]
    ]
    bmi=features["bmi"]
    exercise=features["exercise_minutes_per_day"]
    sleep=features["sleep_hours"]
    stress=features["stress_level"]
    sugar=features["sugar_intake"] 
    smoking=features["smoking_status"] 
    sitting=features["sitting_hours_per_day"] 
    alcohol=features["alcohol_consumption"] 
    fast_food=features["fast_food_intake"] 
    fruit=features["fruit_intake"] 
    fiber=features["fiber_intake"] 
    disease_factors = {
        "hypertension_risk": [
            {"name": "BMI", "level": get_factor_level(bmi, 25, 30)},
            {"name": "Physical Activity", "level": get_factor_level(exercise, 1, 3)},
            {"name": "Sleep Duration", "level": get_factor_level(sleep, 5, 7)},
            {"name": "Stress Level", "level": get_factor_level(stress, 1, 2)},
        ],
        "diabetes_risk": [
            {"name": "Sugar Intake", "level": get_factor_level(sugar, 1, 3)},
            {"name": "BMI", "level": get_factor_level(bmi, 25, 30)},
            {"name": "Exercise", "level": get_factor_level(exercise, 1, 3)},
        ],
        "heart_disease_risk": [
            {"name": "Age", "level": get_factor_level(age, 40, 55)},
            {"name": "Physical Activity", "level": get_factor_level(exercise, 1, 3)},
            {"name": "Sitting Hours", "level": get_factor_level(sitting, 4, 7)},
            {"name": "Stress Level", "level": get_factor_level(stress, 1, 2)},
            {"name": "Sleep Duration", "level": get_factor_level(sleep, 5, 7)},
            {"name": "Smoking", "level": get_factor_level(smoking, 0, 1)},
            {"name": "Alcohol Consumption", "level": get_factor_level(alcohol, 0, 1)},
        ],

        "obesity_risk": [
                {"name": "BMI", "level": get_factor_level(bmi, 25, 30)},
                {"name": "Fast Food Intake", "level": get_factor_level(fast_food, 1, 3)},
                {"name": "Physical Activity", "level": get_factor_level(exercise, 1, 3)},
                {"name": "Sitting Hours", "level": get_factor_level(sitting, 4, 7)},
                {"name": "Sleep Duration", "level": get_factor_level(sleep, 5, 7)},
            ],
    }
    #  GET EXISTING DISEASES FROM DB
    existing = models.getDiseasesUser(userid)  # you create this
    #existing_diseases = [d["disease"].lower() for d in existing]
    existing_diseases= [d["disease"].lower() for d in existing]
    # Example mapping safety
    existing_diseases1 = [
        d.replace(" ", "_") for d in existing_diseases
    ]

    #  GENERATE RECOMMENDATIONS
    recommendations = generate_full_recommendations(ml_result, existing_diseases)

     
    print("disease factors")
    print(disease_factors)
    # Normalize DB diseases
    print("existing")
    print(existing_diseases)
    existing_diseases = [
        d.strip().lower().replace(" ", "_")
        for d in existing_diseases
    ]
    for disease, data in ml_result.items():
        clean_name = disease.replace("_risk", "").strip().lower()
        print(clean_name)
        print(existing_diseases)
        if clean_name in existing_diseases:
            data["already_exists"] = True
        else:
            data["already_exists"] = False
    print("+++++++++++++++++++++")
    print(ml_result)
    return render(request, "lifestyle_analysis_result.html", {
        "lifestyle": lifestyle_data,
        "result": ml_result,
        "high_risks": high_risks,
        "disease_factors": disease_factors,
        "recommendations":recommendations,
        "existing_diseases": existing_diseases
    })
def analyze_lifestyle2(request):
    userid = request.session["userid"]

    if not userid:
        return redirect("/login/")

    # Check lifestyle data
    lifestyle_exists = models.checkLifestyleExists(userid)

    if not lifestyle_exists:
        # Lifestyle not filled
        return redirect("/lifestyle/")

    # Fetch lifestyle data
    lifestyle_data = models.getLifestyleByUser(userid)

    # Check chronic disease data
    #chronic_exists = models.checkChronicDiseaseExists(userid)

    #if not chronic_exists:
       # return redirect("/diseases/")

    # ---------- ML ANALYSIS PLACEHOLDER ----------
    # ml_result = analyze_lifestyle_ml(lifestyle_data)
    ml_result = {
        "diabetes_risk": "Moderate",
        "heart_disease_risk": "Low",
        "obesity_risk": "High"
    }

    return render(request, "lifestyle_analysis_result.html", {
        "lifestyle": lifestyle_data,
        "result": ml_result
    })
# ---------------------------
# MANAGE SYMPTOMS PAGE
# ---------------------------
def manageSymptoms(request):
    msg = ""

    if request.method == "POST":
        symptom_name = request.POST.get("symptom_name")

        if not symptom_name:
            msg = "Symptom name required"
        elif models.symptomExists(symptom_name):
            msg = "Symptom already exists"
        else:
            if models.addSymptom(symptom_name):
                msg = "Symptom added successfully"
            else:
                msg = "Error adding symptom"

    symptoms = models.getAllSymptoms()

    return render(
        request,
        "manageSymptoms.html",
        {
            "symptoms": symptoms,
            "msg": msg
        }
    )
def manageDiseaseSymptoms(request):
    msg = ""

    if request.method == "POST":
        disease_id = request.POST.get("disease_id")
        symptom_ids = request.POST.getlist("symptom_ids")

        if disease_id and symptom_ids:
            models.addDiseaseSymptomMapping(disease_id, symptom_ids)
            msg = "Disease–Symptom mapping saved successfully"
    speciality=request.session["speciality"]
    diseases = models.getAllDiseases()
    symptoms = models.getAllSymptoms()
    mappings = models.getDiseaseSymptomMap(speciality)

    return render(request, "manage_disease_symptoms.html", {
        "diseases": diseases,
        "symptoms": symptoms,
        "mappings": mappings,
        "msg": msg
    })
def manageDoctorDiseases(request):
    msg = ""
    doctor_userid = request.session["userid"]
    # DELETE
    if request.method == "GET" and request.GET.get("delete_id"):
        did = request.GET.get("delete_id")
        models.deleteDoctorDiseaseMapping(did)
        msg = "Disease deleted successfully"

    if request.method == "POST":
        
        disease_ids = request.POST.getlist("disease_ids")

        if doctor_userid and disease_ids:
            models.addDoctorDiseaseMapping(doctor_userid, disease_ids)
            msg = "Doctor–Disease mapping saved successfully"

     
    diseases = models.getAllDiseases()
    mappings = models.getDoctorDiseaseMap(doctor_userid)

    return render(request, "manage_doctor_diseases.html", { 
        "diseases": diseases,
        "mappings": mappings,
        "msg": msg
    })

def manageCommonDiseases(request):
    msg = ""

    # DELETE
    if request.method == "GET" and request.GET.get("delete_id"):
        disease_id = request.GET.get("delete_id")
        models.deleteCommonDisease(disease_id)
        msg = "Disease deleted successfully"

    # ADD
    if request.method == "POST":
        disease_name = request.POST.get("disease_name")
        speciality = request.POST.get("speciality")

        models.addCommonDisease(disease_name, speciality)
        msg = "Disease added successfully"
    speciality = request.session["speciality"]
    diseases = models.getCommonDiseases(speciality.strip())

    return render(request, "manage_common_diseases.html", {
        "diseases": diseases,
        "msg": msg
    })

def doctorDetails(request):
    userid=request.GET.get("userid")
    print(userid)
    doctor = models.getDoctorDetails1(userid)
    reviews = models.getDoctorReviews(userid)
    print(doctor)
    return render(request, "doctor_details.html", {
        "doctor": doctor,
        "reviews": reviews
    })
def submitDoctorReview(request):
    if request.method == "POST":
        doctor = request.POST.get("doctor_userid")
        rating = request.POST.get("rating")
        review = request.POST.get("review")

        user = request.session["userid"]

        models.addDoctorReview(doctor, user, rating, review)

        return JsonResponse({
            "status": "success",
            "message": "Review submitted successfully"
        })
def manage_recommendations(request):
    folder_path = os.path.join(settings.BASE_DIR, "static/recommendations")

    #   READ ALL CSV FILES
    csv_data = {}

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)

            try:
                df = pd.read_csv(file_path)

                # Convert to list for template
                csv_data[file] = {
                    "columns": df.columns.tolist(),
                    "rows": df.head(100).values.tolist()   # limit for performance
                }

            except Exception as e:
                print("Error reading:", file, e)

    # ⬆ FILE UPLOAD
    if request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if uploaded_file:
            file_name = uploaded_file.name

            save_path = os.path.join(folder_path, file_name)

            #   REPLACE existing file
            with open(save_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

        return redirect("/manage-recommendations/")

    return render(request, "admin_recommendations.html", {
        "csv_data": csv_data
    })