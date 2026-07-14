from django import forms
from .models import StudentProfile


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile

        fields = [
            "full_name",
            "student_id",
            "school",
            "faculty",
            "department",
            "program",
            "academic_year",
        ]

        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "student_id": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "school": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "faculty": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "department": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "program": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "academic_year": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }