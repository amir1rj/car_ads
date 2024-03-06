
import re
from rest_framework import serializers

def is_not_mobile_phone(value):
    """
    Validate the phone number based on Iranian format
    :param: a string
    :return: True/False
    """
    patter1 = re.compile("^9\d{9}$")
    patter2 = re.compile("^09\d{9}$")
    patter3 = re.compile("^00989\d{9}$")
    patter4 = re.compile("^\+989\d{9}$")
    if bool(patter1.match(value)) or bool(patter2.match(value)) or bool(patter3.match(value)) or bool(
            patter4.match(value)):

        raise serializers.ValidationError("Please enter static phone numbers only. Mobile numbers are not allowed.")
    else:
        return value
