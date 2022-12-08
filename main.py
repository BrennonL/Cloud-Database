'''
Brennon Laney
Sprint 5 Cloud Database
'''

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def initialize_firestore():

    # This grabs the firestore cloud using the credentials/ keys
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloud-database-test-9e44a-firebase-adminsdk-l2wkz-316ce5c5d1.json"
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        "projectID": "cloud-database-test-9e44a"
    })

    db = firestore.client()

    return db

def add_new_student(db):
    ''''''
    # This asks the user for information on the student that they want to put in the database
    student_name = input("Name of the student: ")
    math_grade = float(input("Math grade (points 0-100): "))
    science_grade = float(input("Science grade (points 0-100) "))
    history_grade = float (input("History grade (points 0-100 "))
    english_grade = float(input("English grade (points 0-100) "))

    # This will check to see if the the student exists in the current database
    item = db.collection("inventory").document(student_name).get()
    if item.exists:
        print("That student already exists in the system")
        return

    # Else is will add the information to the database 
    else:
        grades = {"math_grd": math_grade,
        "science_grd": science_grade,
        "history_grd": history_grade,
        "english_grd": english_grade}

        db.collection("inventory").document(student_name).set(grades)

    # For spacing
    print()
    print()
    

def change_grade(db):
    '''
    This function grabs the students name that the user selects and allows the
    user to also select a class that they are able to change
    return: Void
    '''
    
    # This will print out each students' names
    students = db.collection("inventory").get()
    for student in students:
        print(student.id)

    # Grab the user's input on what student's grade they want to change
    student_name = input("Which student's grade do you want to modify? ")


    result = db.collection("inventory").document(student_name).get()
    if result.exists:
        index = 1
        result = result.to_dict()

        # This will display each of the different classes that the user can change the grades for
        for grade in result:
            print(f"{index}.) {grade}")
            index += 1
        
        # Based on which option the user selects, allow them to change a class's grade
        run = True
        while run == True:
            choice = input("which grade do you want to modify?(0-4) ")
            if choice == "0":
                run = False
            elif choice == "3":
                changed_grade = float(input("What is the new English grade? "))
                result["english_grd"] = changed_grade
            elif choice == "2":
                changed_grade = float(input("What is the new History grade? "))
                result["history_grd"] = changed_grade
            elif choice == "4":
                changed_grade = float(input("What is the new Math grade? "))
                result["math_grd"] = changed_grade
            elif choice == "1":
                changed_grade = float(input("What is the new Science grade? "))
                result["science_grd"] = changed_grade
            else:
                print("That is not a valid option, please type a number 0-4")
                print()
            db.collection("inventory").document(student_name).set(result)
    else:
        print("That student doesn't exist")

    # For spacing 
    print()
    print()



def display_student_GPA(db):
    '''
    This function will grab all the student's names from the firebase database
    and print them out
    '''
    students = db.collection("inventory").get()

    # This will grab all of the students each individual gpas for each grade 
    for student in students:
        student_dic = student.to_dict()
        math_grd = student_dic["math_grd"]
        science_grd = student_dic["science_grd"]
        history_grd = student_dic["history_grd"]
        english_grd = student_dic["english_grd"]
        
        # This will calculate the individual gpa by finding the mean of all the gpas 
        #and it will print it out
        gpa = calculate_gpa(math_grd, science_grd, history_grd, english_grd)
        print(f"{student.id}, GPA: {gpa:.1f}")
    
    # For spacing
    print()
    print()

def display_class_GPA(db):
    ''''''
    students = db.collection("inventory").get()
    total_gpa = 0
    for student in students:
        student_dic = student.to_dict()

        math_grd = student_dic["math_grd"]
        science_grd = student_dic["science_grd"]
        history_grd = student_dic["history_grd"]
        english_grd = student_dic["english_grd"]
        gpa = calculate_gpa(math_grd, science_grd, history_grd, english_grd)
        total_gpa += gpa
        
    class_gpa = total_gpa / len(students)
    print(f"The classes overall GPA is: {class_gpa:.1f}")
    print()
    print()


def calculate_gpa(math_grd, science_grd, history_grd, english_grd):
    '''
    This will take the grades and find the gpa for each. It will then calculate
    the mean gpa
    return: gpa_total
    '''

    # This is a dictionary so that this function can store each gpa point for each grade
    grades = {
        math_grd : 0,
        science_grd : 0,
        history_grd : 0,
        english_grd :0 
    }

    
    for grade in grades:
        if grade >= 94:
            gpa = 4.0
        elif grade >= 90:
            gpa = 3.7
        elif grade >= 87:
            gpa = 3.3
        elif grade >= 84:
            gpa = 3.0
        elif grade >= 80:
            gpa = 2.7
        elif grade >= 77:
            gpa = 2.3
        elif grade >= 74:
            gpa  = 2.0
        elif grade >= 70:
            gpa = 1.7
        elif grade >= 67:
            gpa = 1.3
        elif grade >= 64:
            gpa= 1.0
        elif grade >= 60:
            gpa = 0.7
        else:
            gpa = 0
        grades[grade] = gpa

    # This will add the gpas together and divide by 4 to find the total gpa
    gpa_total = 0
    total = 0
    for grade in grades:
        total = total + grades[grade]

    gpa_total = total / 4
    return gpa_total

def notify_low_grade(results, changes, read_time):
    '''
    This function will detect any changes to the database and alert the user
    Return: Nothing
    '''
    for change in changes:
        if change.type.name == "ADDED":
            print()
            print(f"GRADE TOO LOW! ENCOURAGE {change.document.id} MORE")
            print()
        elif change.type.name == "REMOVED":
            print()
            print("GRADE FIXED")


def grade_too_low(db):
    '''
    This function will call the notify user, if any of the grades drop too low
    '''
    db.collection("inventory").where("english_grd", "<=", 50).on_snapshot(notify_low_grade)
    db.collection("inventory").where("science_grd", "<=", 50).on_snapshot(notify_low_grade)
    db.collection("inventory").where("history_grd", "<=", 50).on_snapshot(notify_low_grade)
    db.collection("inventory").where("math_grd", "<=", 50).on_snapshot(notify_low_grade)

def main():
    db = initialize_firestore()

    # This will notify the user if one of the student's grades drops too low
    grade_too_low(db)

    # Ask the user for which option they want to do
    choice = None
    while choice != "0":
        print("(0) Quit")
        print("(1) Add a new student")
        print("(2) Change grade")
        print("(3) Display students GPA")
        print("(4) Display class GPA")
        choice = input("Please select one of these (0-4): ")

        # if the user selected 1 then the add_new_student function is called
        if choice == "1":
            add_new_student(db)

        # if the user selected 2 then the change_grade function is called
        elif choice == "2":
            change_grade(db)

        # if the user selected 3 then the display_student_GPA function is called
        elif choice == "3":
            display_student_GPA(db)

        # If the user selected 4 then the function display_class_GPA is called
        elif choice == "4":
            display_class_GPA(db)
        
        # For spacing
        print()
        print()

if __name__ == "__main__":
    main()