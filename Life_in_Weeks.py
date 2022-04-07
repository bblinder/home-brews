#!/usr/bin/env python3

"""
Based on Tim Urban's Life in Weeks blog post on Wait-but-why: https://waitbutwhy.com/2014/05/life-weeks.html
"""

age = input("What is your current age? --> ")

def calculate_life_in_weeks(age):
    years = 90 - int(age)
    months = round(years * 12)
    weeks = round(years * 52)
    days = round(years * 365)
    
    print(f"You have {days} days, {weeks} weeks, and {months} months left")

if __name__ == "__main__":
    calculate_life_in_weeks(age)