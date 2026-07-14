import profile
from annotated_types import doc
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from jmespath.functions import signature
from .models import Post, Comment, CGPARecord, GPARecord, Assignment, Course, TimetableEntry, StudySession, Profile, AIStudyHistory, AIUsage, AIWallet, PaidTransaction
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, request
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from reportlab.platypus import HRFlowable, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer)
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import google.generativeai as genai, os, hashlib, requests, hmac
from django.core.cache import cache
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_bytes
from decimal import Decimal
from django.core.mail import send_mail
import numpy as np
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image
from .models import StudentProfile
from .forms import StudentProfileForm
from reportlab.platypus.flowables import HRFlowable
import qrcode
from io import BytesIO
from reportlab.platypus import Image
from reportlab.platypus import KeepTogether

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Create your views here.
@never_cache
def index(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

    # Validate required fields
        if not full_name or not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required')
            return redirect('index')

    # Password match check
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('index')

    # Check if username OR email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('index')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('index')


        user = User.objects.create_user(
            
            username=username,
            email=email,
            password=password1
        )

        first_name = full_name.split()[0]
        user.first_name = first_name
        user.save()
        
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.modified = True
        messages.success(request, 'Account created successfully')
        return redirect('index')
    
    context = {
        'recent_posts': Post.objects.all().order_by('-created_at')[:3],
        'courses' : Course.objects.all().order_by('-created_at')[:6],
    }

    return render(request, 'index.html',
        context
)
    

def about(request):
    return render(request, 'about.html')


def blog(request):
    all_posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(all_posts, 6)  # 6 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog.html', {'posts': page_obj})

def blog_single(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'blog-single.html', {'post': post})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
New Contact Message

Name: {name}
Email: {email}

Message:
{message}
"""

        try:
            # 1. SEND TO ADMIN (YOU)
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            # 2. AUTO REPLY TO USER
            send_mail(
                subject="We received your message",
                message="""
                Hello,

                Thank you for contacting Ichason Study Hub.

                We received your message and will respond as soon as possible.

                Regards,
                Ichason Team
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Message sent successfully!")

        except Exception as e:
            print("EMAIL ERROR:", e)
            messages.error(request, "Email failed to send.")

        return redirect("contact")

    return render(request, "contact.html")
# ------->  USER PROFILE CREATION <-------

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        

def gpa_calculator(request):

    records = []

    if request.user.is_authenticated:
        records = GPARecord.objects.filter(
            user=request.user
        ).order_by('-created_at')

    return render(request, 'gpa calculator.html', {
        'records': records
    })

    # ----> Courses <-------
def courses(request):
    all_courses = Course.objects.all()

    paginator = Paginator(all_courses, 6)  # 6 courses per page
    page_number = request.GET.get("page")
    courses = paginator.get_page(page_number)

    return render(request, "courses.html", {
        "courses": courses
    })
    
def course_detail(request, id):
    course = get_object_or_404(Course, id=id)

    context = {
        'course': course
    }

    return render(request, 'course_detail.html', context)
        
def cgpa_calculator(request):
    return render(request, 'cgpa calculator.html')
def exam_score_predict(request):
    return render(request, 'exam score predict.html')


# -------> TIME TABLE <-------

@login_required
def time_table_builder(request):

    if request.method == "POST":
        TimetableEntry.objects.create(
            user=request.user,
            course=request.POST.get("course"),
            day=request.POST.get("day"),
            start_time=request.POST.get("start_time"),
            end_time=request.POST.get("end_time"),
            venue=request.POST.get("venue"),
        )
        return redirect("time table builder")

    entries = list(
        TimetableEntry.objects.filter(user=request.user)
        .order_by("day", "start_time")
    )

    # ORDER DAYS PROPERLY
    day_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
    }

    entries.sort(
        key=lambda x: (day_order.get(x.day, 99), x.start_time)
    )

    # 👇 REMOVE REPEATED DAY LABELS
    last_day = None

    for entry in entries:
        if entry.day != last_day:
            entry.display_day = entry.day
            last_day = entry.day
        else:
            entry.display_day = ""   # blank for same day rows

    return render(
        request,
        "time table builder.html",
        {"entries": entries}
    )
    
@login_required
def download_timetable(request):
   
    time_format = request.GET.get("time_format", "24")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_timetable.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("MY CLASS TIMETABLE", styles['Title']))
    elements.append(Spacer(1, 15))

    format_text = "12 Hour Format (AM/PM)" if time_format == "12" else "24 Hour Format"
    elements.append(Paragraph(f"Time Format: {format_text}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # ORDER DAYS PROPERLY
    DAY_ORDER = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
    }

    entries = list(
        TimetableEntry.objects.filter(user=request.user)
    )

    # sort by day + time
    entries.sort(
        key=lambda x: (
            DAY_ORDER.get(x.day, 99),
            x.start_time
        )
    )

    # TABLE HEADER
    data = [["Course", "Day", "Start", "End", "Venue"]]

    last_day = None

    for entry in entries:

        # FORMAT TIME
        if time_format == "12":
            start = entry.start_time.strftime("%I:%M %p")
            end = entry.end_time.strftime("%I:%M %p")
        else:
            start = entry.start_time.strftime("%H:%M")
            end = entry.end_time.strftime("%H:%M")

        # ONLY SHOW DAY ONCE
        if entry.day != last_day:
            day_display = entry.day
            last_day = entry.day
        else:
            day_display = ""   # 👈 THIS IS THE MAGIC

        data.append([
            entry.course,
            day_display,
            start,
            end,
            entry.venue
        ])
        
    

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 30),
        ('RIGHTPADDING', (0, 0), (-1, -1), 30),
    ]))

    elements.append(table)

    doc.build(elements)

    return response


# --------> Single DELETE  <----------

@login_required
@require_POST
def delete_timetable(request, id):

    if request.method == "POST":
        entry = get_object_or_404(TimetableEntry, id=id, user=request.user)
        entry.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid method"}, status=400)

# -------> CLEAR ALL TIMETABLE  <----------

@login_required
@require_POST
def delete_all_timetables(request):

    if request.method == "POST":
        TimetableEntry.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid method"}, status=400)


# --------> TIME TABLE ENDS <-----------
    

def study_timer(request):

    records = []
    sessions = []
    total_minutes = 0
    session_count = 0
    streak = 0
    last_study_date = None

    if request.user.is_authenticated:

        # Get all sessions
        sessions = StudySession.objects.filter(
            user=request.user
        ).order_by('-created_at')

        today = timezone.now().date()

        # Today's sessions only
        today_sessions = StudySession.objects.filter(
            user=request.user,
            created_at__date=today
        )

        total_minutes = sum(
            session.duration for session in today_sessions
        )

        session_count = today_sessions.count()

        # ✅ SAFE PROFILE ACCESS (FIX)
        profile, created = Profile.objects.get_or_create(user=request.user)

        streak = profile.streak
        last_study_date = profile.last_study_date

    return render(
        request,
        'study timer.html',
        {
            'sessions': sessions,
            'total_minutes': total_minutes,
            'session_count': session_count,
            'streak': streak,
            'last_study_date': last_study_date,
            'records': records,
        }
    )
    
    
@login_required
@require_POST
def save_study_session(request):
    try:
        # =========================
        # 1. PARSE REQUEST DATA
        # =========================
        data = json.loads(request.body or "{}")

        subject = data.get("subject", "").strip()
        goal = data.get("goal", "").strip()
        duration = data.get("duration")

        # =========================
        # 2. VALIDATION (DO THIS FIRST)
        # =========================
        if not subject or not goal:
            return JsonResponse({
                "status": "error",
                "message": "Subject and goal are required"
            }, status=400)

        try:
            duration = int(duration)
        except (TypeError, ValueError):
            duration = 25  # fallback default

        # =========================
        # 3. CREATE STUDY SESSION
        # =========================
        session = StudySession.objects.create(
            user=request.user,
            subject=subject,
            goal=goal,
            duration=duration,
            completed=True
        )

        # =========================
        # 4. STREAK LOGIC (FIXED + SAFE)
        # =========================
        profile, _ = Profile.objects.get_or_create(user=request.user)

        today = date.today()

        if profile.last_study_date:
            if profile.last_study_date == today:
                pass  # already counted today

            elif profile.last_study_date == today - timedelta(days=1):
                profile.streak += 1  # continue streak

            else:
                profile.streak = 1  # reset streak

        else:
            profile.streak = 1

        profile.last_study_date = today
        profile.save()

        # =========================
        # 5. RESPONSE
        # =========================
        return JsonResponse({
            "status": "success",
            "id": session.id,
            "streak": profile.streak
        })

    # =========================
    # 6. ERROR HANDLING
    # =========================
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON"
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
        
# -------> SINGLE DELETE STUDY TIMER <---------
@login_required
@require_POST
def delete_study_session(request, id):

    session = get_object_or_404(
        StudySession,
        id=id,
        user=request.user
    )

    session.delete()

    return JsonResponse({"success": True})

# -------> CLEAR ALL STUDY TIMER  <---------
@login_required
@require_POST
def clear_study_sessions(request):

    StudySession.objects.filter(user=request.user).delete()

    return JsonResponse({"success": True})

# -------> END OF STUDY TIMER <---------

@login_required
def ai_note_summarizer(request):
        history = (
        AIStudyHistory.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

        paginator = Paginator(history, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "ai note summarizer.html", {
            "page_obj": page_obj
    })
def privacy_policy(request):
    return render(request, "privacy_policy.html")
def refund_policy(request):
    return render(request, "refund_policy.html")
def Terms_and_Conditions(request):
    return render(request, "terms_and_conditions.html")

@login_required
@require_POST
def add_comment(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)

        Comment.objects.create(
            post=post,
            user=request.user,   # ✅ logged-in user
            content=request.POST['content']
        )
    return redirect('blog')


#""" Only logged in user can see their saved calculations (CGPA PAGE) """

@login_required
def save_cgpa(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body or "{}")
        cgpa = data.get("cgpa")
        total_units = data.get("total_units")
        semesters = data.get("semesters", [])

        if cgpa is None or total_units is None:
            return JsonResponse({"error": "Missing data"}, status=400)

        record = CGPARecord.objects.create(
            user=request.user,
            cgpa=float(cgpa),
            total_units=int(total_units),
            semesters=semesters,
            classification=data["classification"],
        )

        return JsonResponse({
            "message": "Saved successfully",
            "data": {
                "cgpa": record.cgpa,
                "total_units": record.total_units,
                "classification": record.classification,
                "id": record.id,
                "semesters": record.semesters 
            }
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    
    #""" SHOW USER HISTORY (CGPA PAGE) """

def cgpa_page(request):
    records = []
    
    if request.user.is_authenticated:
        records = CGPARecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cgpa calculator.html', {
        'records': records
    })
    
    # --------> delete_cgpa <----------
@login_required
def delete_cgpa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        record = CGPARecord.objects.get(id=pk, user=request.user)
        record.delete()

        return JsonResponse({
            "message": "CGPA record deleted",
            "id": pk
        })

    except CGPARecord.DoesNotExist:
        return JsonResponse({"error": "Record not found"}, status=404)
    
    # --------------> END OF CGPA <-------------

# ---------> GPA SAVE RECORD <---------
@login_required
def save_gpa(request):
    
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body)
        gpa = data.get("gpa")
        total_units = data.get("total_units")
        classification = data.get("classification")
        courses = data.get("courses") or []

        if gpa is None or total_units is None:
            return JsonResponse({"error": "Missing data"}, status=400)

        record=GPARecord.objects.create(
            user=request.user,
            gpa=float(gpa),
            total_units=int(total_units),
            classification=classification or "-",
            courses=courses
        )

        return JsonResponse({
        "message": "GPA saved successfully",
        "data": {
        "id": record.id,
        "gpa": record.gpa,
        "total_units": record.total_units,
        "classification": record.classification,
        "courses": record.courses
    }
})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
@login_required
def gpa_page(request):
    records = GPARecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'gpa calculator.html', {
        'records': records
    })
    

    # -------> delete_gpa <--------
    
@login_required
def delete_gpa(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    try:
        record = GPARecord.objects.get(id=pk, user=request.user)
        record.delete()

        return JsonResponse({
            "message": "GPA record deleted",
            "id": pk
        })

    except GPARecord.DoesNotExist:
        return JsonResponse({"error": "Record not found"}, status=404)
    
    
    
    # =========================
# FOOTER FUNCTION (CANVAS)
# =========================
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)

    canvas.drawCentredString(
        doc.pagesize[0] / 2,
        20,
        "All rights reserved | Ichason—Lab"
    )

    canvas.restoreState()
    
    # --------> PDF DOWNLOADER <--------
@login_required
def student_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("download_transcript")

    else:
        form = StudentProfileForm(
            instance=profile
        )

    return render(
        request,
        "student_profile.html",
        {
            "form": form
        }
    )
def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        box_size=4,
        border=2
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return Image(buffer, width=80, height=80)
    
# ================= FOOTER / DECORATION =================
def add_footer(canvas, doc):
    canvas.saveState()

    # Curved footer
    canvas.setFillColor(colors.darkblue)

    path = canvas.beginPath()
    path.moveTo(0, 50)
    path.curveTo(150, 0, 450, 100, 600, 50)
    path.lineTo(600, 0)
    path.lineTo(0, 0)
    path.close()

    canvas.drawPath(path, fill=1, stroke=0)

    # Footer text
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(30, 15, "Ichason Transcript System")

    canvas.restoreState()

# ================= GOLD DIVIDER =================
gold_line = HRFlowable(
    width="100%",
    thickness=2,
    color=colors.HexColor("#D4AF37")
)


@login_required
def download_transcript(request):
    profile = StudentProfile.objects.filter(user=request.user).first()

    full_name = profile.full_name if profile else "N/A"
    student_id = profile.student_id if profile else "N/A"
    school = profile.school if profile else "N/A"
    faculty = profile.faculty if profile else "N/A"
    department = profile.department if profile else "N/A"
    academic_year = profile.academic_year if profile else "N/A"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transcript.pdf"'

    doc = SimpleDocTemplate(
        response,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=50
    )

    elements = []

    # ================= STYLES =================
    TITLE = ParagraphStyle(
        "TITLE",
        fontSize=20,
        leading=24,
        alignment=1,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1f4e79"),
    )

    SUBTITLE = ParagraphStyle(
        "SUBTITLE",
        fontSize=10,
        alignment=1,
        textColor=colors.grey,
        spaceAfter=10,
    )

    SECTION = ParagraphStyle(
        "SECTION",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1f4e79"),
        spaceBefore=10,
        spaceAfter=6,
    )

    LABEL = ParagraphStyle("LABEL", fontSize=10, fontName="Helvetica-Bold")
    VALUE = ParagraphStyle("VALUE", fontSize=10)

    VERIFY = ParagraphStyle(
        "VERIFY",
        fontSize=9,
        alignment=1,
        textColor=colors.grey,
    )

    # ================= HEADER =================
    logo = Image("static/img/ICHASON-LAB.jpeg", width=60, height=60)
    signature = Image("static/img/signature.png", width=70, height=40)
    
    date_text = Paragraph(
    datetime.now().strftime("%d %B %Y"),
    ParagraphStyle(
        "DateStyle",
        fontSize=9,
        alignment=1,  # center
        textColor=colors.grey
    )
)
    right_block = Table([
    [signature],
    [date_text]
], colWidths=[80])
    
    header = Table([
    [
        logo,
        Paragraph("ICHASON-LAB TRANSCRIPT", TITLE),
        right_block
    ]
], colWidths=[70, doc.width - 140, 70])

    header.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(header)
    elements.append(Paragraph("Official Academic Record & Performance Summary", SUBTITLE))

    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#1f4e79")))
    elements.append(Spacer(1, 15))

    # ================= STUDENT INFO =================
    transcript_no = f"ICH-{request.user.id}-{datetime.now().year}"
    issue_date = datetime.now().strftime("%d %B %Y")

    def row(k, v):
        return [Paragraph(k, LABEL), Paragraph(str(v), VALUE)]

    info_table = Table([
        row("Full Name", full_name),
        row("Student ID", student_id),
        row("Institution", school),
        row("Faculty", faculty),
        row("Department", department),
        row("Academic Year", academic_year),
        row("Transcript No", transcript_no),
        row("Date Issued", issue_date),
    ], colWidths=[140, doc.width - 140])

    info_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(Paragraph("STUDENT INFORMATION", SECTION))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # ================= GPA =================
    gpa_data = [["Courses", "GPA", "Units", "Class", "Date"]]

    gpa_records = GPARecord.objects.filter(user=request.user)

    for r in gpa_records:
        try:
            courses = json.loads(r.courses) if isinstance(r.courses, str) else r.courses
        except:
            courses = []

        course_text = "<br/>".join(
    f"{c.get('course')} ({c.get('unit')})"
    for c in courses if isinstance(c, dict)
)

        gpa_data.append([
            smart_cell(course_text),
            f"{r.gpa:.2f}",
            r.total_units,
            r.classification,
            r.created_at.strftime("%d-%m-%Y")
        ])

    gpa_table = Table(gpa_data, colWidths=[
        doc.width * 0.35,
        doc.width * 0.12,
        doc.width * 0.12,
        doc.width * 0.18,
        doc.width * 0.23,
    ],
      repeatRows=1                
)

    gpa_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.white),
        ("LINEBELOW", (0, 1), (-1, -1), 0.2, colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))

    elements.append(Paragraph("GPA HISTORY", SECTION))
    elements.append(KeepTogether(gpa_table))
    elements.append(Spacer(1, 15))

    # ================= CGPA =================
    cgpa_data = [["Semester", "GPA", "Units", "Class", "Date"]]

    cgpa_records = CGPARecord.objects.filter(user=request.user)

    final_record = cgpa_records.first()

    for r in cgpa_records:
        for s in (r.semesters or []):
            cgpa_data.append([
                f"Semester {s.get('semester')}",
                f"{s.get('gpa'):.2f}",
                s.get('units'),
                "",
                r.created_at.strftime("%d-%m-%Y")
            ])

    if final_record:
        cgpa_data.append([
            "FINAL CGPA",
            f"{final_record.cgpa:.2f}",
            final_record.total_units,
            final_record.classification,
            final_record.created_at.strftime("%d-%m-%Y")
        ])

    # cgpa_table = Table(cgpa_data, colWidths=[
    #     doc.width * 0.3,
    #     doc.width * 0.2,
    #     doc.width * 0.2,
    #     doc.width * 0.3,
    # ])
    
    cgpa_table = Table(
    cgpa_data,
    colWidths=[
        doc.width * 0.24,  # Semester
        doc.width * 0.16,  # CGPA
        doc.width * 0.16,  # Units
        doc.width * 0.22,  # Class
        doc.width * 0.22,  # Date
    ],
    repeatRows=1
)

    cgpa_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.white),
        ("LINEBELOW", (0, 1), (-1, -1), 0.2, colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))

    elements.append(Paragraph("CGPA HISTORY", SECTION))
    elements.append(KeepTogether(cgpa_table))
    elements.append(Spacer(1, 20))

    # ================= QR + VERIFICATION =================
    doc_id = f"ICH-{request.user.id}-{datetime.now().year}"
    verification_url = request.build_absolute_uri(f"/verify-transcript/?doc_id={doc_id}")
    qr_code = generate_qr(verification_url)

    verification_box = Table([[
        Paragraph("VERIFICATION SUMMARY", SECTION),
        Paragraph(f"Doc ID: {doc_id}", VERIFY),
        Paragraph(f"Total Units: {sum([g.total_units for g in gpa_records])}", VERIFY),
        Paragraph("Status: Verified Academic Record", VERIFY),
    ]], colWidths=[doc.width - 30])

    verification_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#1f4e79")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(qr_code)
    elements.append(Paragraph("Scan to verify transcript", VERIFY))
    elements.append(Spacer(1, 10))
    elements.append(verification_box)

    # ================= BUILD =================
    doc.build(
        elements,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    return response


# =========================
# ASSIGNMENT PLANNER
# =========================

@login_required
def assignment_planner(request):
 

    if request.method == "POST":
        Assignment.objects.create(
            user=request.user,
            title=request.POST.get("title"),
            course_code=request.POST.get("course_code"),
            category=request.POST.get("category"),
            priority=request.POST.get("priority"),
            status=request.POST.get("status") or "Not Started",
            progress=request.POST.get("progress") or 0,
            due_date=request.POST.get("due_date")
        )

        return redirect("assignment_planner")

    assignments = Assignment.objects.filter(user=request.user).order_by("due_date")

    today = date.today()

    for a in assignments:
        a.days_left = (a.due_date - today).days

        if a.status == "Completed":
            a.display_status = "Completed ✅"
        else:
            if a.days_left < 0:
                a.display_status = "❌ Overdue"
            elif a.days_left == 0:
                a.display_status = "⚠️ Due Today"
            else:
                a.display_status = "Pending"
        
    today_assignments = [a for a in assignments if a.days_left == 0]
    tomorrow_assignments = [a for a in assignments if a.days_left == 1]

    total = assignments.count()
    completed = assignments.filter(status="Completed").count()
    pending = assignments.exclude(status="Completed").count()
    overdue = assignments.filter(due_date__lt=today).exclude(status="Completed").count()

    return render(request, "assignment planner.html", {
    "assignments": assignments,
    "today_assignments": today_assignments,
    "tomorrow_assignments": tomorrow_assignments,
    "total_assignments": total,
    "completed_count": completed,
    "pending_count": pending,
    "overdue_count": overdue,
    "today": today,
    })


# =========================
# DELETE ALL ASSIGNMENTS
# =========================

@login_required
def delete_all_assignments(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=400)

    Assignment.objects.filter(user=request.user).delete()
    return JsonResponse({"success": True})


# =========================
# UPDATE STATUS
# =========================
@login_required
def update_status(request, id):

    if request.method == "POST":

        assignment = get_object_or_404(
            Assignment,
            id=id,
            user=request.user
        )

        assignment.status = request.POST.get("status")
        assignment.save()

        return JsonResponse({
            "success": True,
            "status": assignment.status
        })

    return JsonResponse(
        {"error": "Invalid method"},
        status=400
    )


# =========================
# DELETE SINGLE ASSIGNMENT
# =========================
@login_required
def delete_assignment(request, id):

    if request.method == "POST":

        assignment = get_object_or_404(
            Assignment,
            id=id,
            user=request.user
        )

        assignment.delete()

        return JsonResponse({"success": True})

    return JsonResponse(
        {"error": "Invalid method"},
        status=400
    )
    
    
    
# =========================
# EDIT ASSIGNMENT
# =========================
@login_required
def edit_assignment(request, id):

    assignment = get_object_or_404(
        Assignment,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        title = request.POST.get("title")
        course_code = request.POST.get("course_code")
        # category = request.POST.get("category")
        priority = request.POST.get("priority")
        status = request.POST.get("status")
        progress = request.POST.get("progress") or 0
        due_date = request.POST.get("due_date")

        # VALIDATION
        if not title:
            messages.error(request, "Assignment title is required.")
            return redirect("assignment planner")

        if not course_code:
            messages.error(request, "Course code is required.")
            return redirect("assignment planner")

        # if not category:
        #     messages.error(request, "Please select a category.")
        #     return redirect("assignment planner")

        if not priority:
            messages.error(request, "Please select a priority.")
            return redirect("assignment planner")

        if not due_date:
            messages.error(request, "Due date is required.")
            return redirect("assignment planner")

        # UPDATE ASSIGNMENT
        assignment.title = title
        assignment.course_code = course_code
        # assignment.category = category
        assignment.priority = priority
        assignment.status = status
        assignment.progress = progress
        assignment.due_date = due_date

        assignment.save()

        messages.success(request, "Assignment updated successfully!")

    return redirect("assignment planner")


# =========================
# Note Summarizer
# =========================

MAX_INPUT_LENGTH = 500

@login_required
@require_POST
def summarize_notes(request):

    try:
        data = json.loads(request.body)
        text = data.get("notes", "").strip()

        if not text:
            return JsonResponse({
                "status": "error",
                "message": "Please enter notes"
            }, status=400)

        # 🚨 CHECK LENGTH LIMIT
        if len(text) > MAX_INPUT_LENGTH:
            return JsonResponse({
                "status": "error",
                "message": f"Input too long. Maximum allowed is {MAX_INPUT_LENGTH} characters."
            }, status=400)

        # =========================
        # ⚡ EXACT CACHE FIRST
        # =========================
        exact_cache_key = (
            "summary_exact_" +
            hashlib.md5(
                text.lower().strip().encode()
            ).hexdigest()
        )

        exact_cached = cache.get(exact_cache_key)

        if exact_cached:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "summary": exact_cached,
                "cached": True,
                "cache_type": "exact",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 🧠 SEMANTIC CACHE SECOND
        # =========================
        cache_key = "semantic_summary_cache"

        cached_summary = semantic_cache_get(
            cache_key,
            text
        )

        if cached_summary:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "summary": cached_summary,
                "cached": True,
                "cache_type": "semantic",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 💰 STRICT AI LIMIT CHECK
        # =========================
        allowed, mode = use_ai_credit(request.user)

        if not allowed:
            return JsonResponse({
                "status": "upgrade_required",
                "message": "You’ve reached your free limit. Upgrade!",
                "detail": "Upgrade your plan to continue using AI tools without interruption.",
                "action": "upgrade"
            }, status=402)

        # =========================
        # 📚 GET CONTEXT HISTORY
        # =========================
        history = AIStudyHistory.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

        history_text = "\n\n".join(
            f"{h.tool_type.upper()}:\nQ: {h.prompt}\nA: {h.response}"
            for h in history
        )

        # =========================
        # 🤖 GEMINI PROMPT
        # =========================
        prompt = f"""
You are a study assistant.

Summarize the notes below in a student-friendly way.

Rules:
- Use HTML only
- Maximum 300 words
- Use <h3> for headings
- Use <p> for explanations
- Use <ul><li> for key points
- Explain each point briefly
- Minimum 100 words
- Do NOT use markdown symbols (*, #, **)

Notes:
{text}
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        summary = response.text

        # =========================
        # 💾 SAVE HISTORY
        # =========================
        AIStudyHistory.objects.create(
            user=request.user,
            tool_type="summarizer",
            prompt=text,
            response=summary
        )

        # =========================
        # 🧹 CLEAN OLD HISTORY
        # =========================
        user_history = AIStudyHistory.objects.filter(
            user=request.user
        ).order_by("created_at")

        if user_history.count() > 1000:

            excess = user_history.count() - 1000

            oldest_ids = user_history.values_list(
                "id",
                flat=True
            )[:excess]

            AIStudyHistory.objects.filter(
                id__in=oldest_ids
            ).delete()

        # =========================
        # 💾 SAVE TO EXACT CACHE
        # =========================
        cache.set(
            exact_cache_key,
            summary,
            timeout=60 * 60
        )

        # =========================
        # 💾 SAVE TO SEMANTIC CACHE
        # =========================
        semantic_cache_set(
            cache_key,
            text,
            summary
        )

        # =========================
        # 🔥 GET UPDATED WALLET
        # =========================
        wallet, _ = AIWallet.objects.get_or_create(
            user=request.user
        )

        remaining = (
            max(0, 3 - wallet.free_used)
            if mode == "free"
            else wallet.paid_credits
        )

        return JsonResponse({
            "status": "success",
            "summary": summary,
            "cached": False,
            "cache_type": None,
            "mode": mode,
            "remaining": remaining
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
        
        
# ----------> Ai CHAT BOT <-----------
@login_required
@require_POST
def generate_quiz(request):

    try:
        data = json.loads(request.body)
        notes = data.get("notes", "").strip()

        if not notes:
            return JsonResponse({
                "error": "No notes provided"
            }, status=400)

        if len(notes) > MAX_INPUT_LENGTH:
            return JsonResponse({
                "status": "error",
                "message": f"Input too long. Maximum allowed is {MAX_INPUT_LENGTH} characters."
            }, status=400)

        # =========================
        # ⚡ EXACT CACHE FIRST
        # =========================
        exact_cache_key = (
            "quiz_exact_" +
            hashlib.md5(
                notes.lower().strip().encode()
            ).hexdigest()
        )

        exact_cached = cache.get(exact_cache_key)

        if exact_cached:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "quiz": exact_cached,
                "cached": True,
                "cache_type": "exact",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 🧠 SEMANTIC CACHE SECOND
        # =========================
        cache_key = "semantic_quiz_cache"

        cached = semantic_cache_get(cache_key, notes)

        if cached:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "quiz": cached,
                "cached": True,
                "cache_type": "semantic",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 💰 STRICT AI CREDIT CHECK
        # =========================
        allowed, mode = use_ai_credit(request.user)

        if not allowed:
            return JsonResponse({
                "status": "upgrade_required",
                "message": "You’ve reached your AI limit. Upgrade!",
                "detail": "Upgrade your plan or buy credits to continue.",
                "action": "upgrade"
            }, status=402)

        # =========================
        # 🤖 GEMINI CALL
        # =========================
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
You are a university professor creating an examination.

Generate 5 challenging questions from the notes provided.

The questions should test:
- Understanding
- Application
- Analysis
- Critical thinking
- Real-world problem solving

Avoid simple definition or recall questions unless necessary.

Question styles should include:
- Scenario-based questions
- Case studies
- "What would happen if..." questions
- Problem-solving questions
- Compare and contrast questions
- Application of concepts to real-life situations

Return ONLY valid HTML.

Structure:

<div class="quiz">

<div class="q">
<h4>Question</h4>
<p>Question text here</p>

<strong>Answer:</strong>
<p>Detailed model answer here</p>
</div>

</div>

Rules:
- No markdown
- No code blocks
- No numbering like 1., 2., 3.
- Each answer should be 2–4 sentences minimum
- Focus on deep understanding
- Use examples where needed

Study Notes:
{notes}
"""

        response = model.generate_content(prompt)
        quiz_text = response.text

        # =========================
        # 💾 SAVE HISTORY
        # =========================
        AIStudyHistory.objects.create(
            user=request.user,
            tool_type="quiz",
            prompt=notes,
            response=quiz_text
        )

        # =========================
        # 🧹 CLEAN OLD HISTORY
        # =========================
        total = AIStudyHistory.objects.filter(
            user=request.user
        ).count()

        if total > 1000:

            excess = total - 1000

            oldest_ids = (
                AIStudyHistory.objects
                .filter(user=request.user)
                .order_by("created_at")
                .values_list("id", flat=True)[:excess]
            )

            AIStudyHistory.objects.filter(
                id__in=oldest_ids
            ).delete()

        # =========================
        # 💾 SAVE TO EXACT CACHE
        # =========================
        cache.set(
            exact_cache_key,
            quiz_text,
            timeout=60 * 60
        )

        # =========================
        # 💾 SAVE TO SEMANTIC CACHE
        # =========================
        semantic_cache_set(
            cache_key,
            notes,
            quiz_text
        )

        # =========================
        # 🔥 WALLET STATUS
        # =========================
        wallet, _ = AIWallet.objects.get_or_create(
            user=request.user
        )

        remaining = (
            max(0, 3 - wallet.free_used)
            if mode == "free"
            else wallet.paid_credits
        )

        return JsonResponse({
            "status": "success",
            "quiz": quiz_text,
            "cached": False,
            "cache_type": None,
            "mode": mode,
            "remaining": remaining
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)


def can_use_ai(user):
    today = date.today()

    usage, created = AIUsage.objects.get_or_create(
        user=user,
        date=today,
        defaults={"count": 0}
    )

    return usage.count < 5, usage

# =========================
# AI HISTORY
# =========================
    
@login_required
def history_detail(request, pk):
    item = get_object_or_404(
        AIStudyHistory,
        id=pk,
        user=request.user
    )
    
    user_history = (
    AIStudyHistory.objects
    .filter(user=request.user)
    .order_by("-created_at")
)

    if user_history.count() > 1000:
        ids_to_keep = user_history.values_list("id", flat=True)[:1000]
        user_history.exclude(id__in=ids_to_keep).delete()
    # if AIStudyHistory.objects.filter(user=request.user).count() > 1000:

    return render(request, "history_detail.html", {
        "item": item
    })

# =========================
#  CLEAR AI HISTORY
# =========================
@login_required
@require_POST
def clear_aihistory(request):

    AIStudyHistory.objects.filter(
        user=request.user
    ).delete()

    return JsonResponse({
        "success": True
    })
    
def get_ai_context(user, limit=10):
    history = AIStudyHistory.objects.filter(
        user=user
    ).order_by("-created_at")[:limit]

    return "\n\n".join(
        f"{h.tool_type.upper()}:\nQ: {h.prompt}\nA: {h.response}"
        for h in history
    )
    
    

# EXPLAIN TOPIC
# -------------------------
@login_required
@require_POST
def explain_topic(request):

    try:
        data = json.loads(request.body or "{}")
        text = data.get("topic", "").strip()

        if not text:
            return JsonResponse({
                "status": "error",
                "message": "Topic is required"
            }, status=400)

        if len(text) > MAX_INPUT_LENGTH:
            return JsonResponse({
                "status": "error",
                "message": f"Input too long. Maximum allowed is {MAX_INPUT_LENGTH} characters."
            }, status=400)

        # =========================
        # ⚡ EXACT CACHE FIRST
        # =========================
        exact_cache_key = (
            "explain_exact_" +
            hashlib.md5(
                text.lower().strip().encode()
            ).hexdigest()
        )

        exact_cached = cache.get(exact_cache_key)

        if exact_cached:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "explanation": exact_cached,
                "cached": True,
                "cache_type": "exact",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 🧠 SEMANTIC CACHE SECOND
        # =========================
        cache_key = "semantic_explain_cache"

        cached_explanation = semantic_cache_get(
            cache_key,
            text
        )

        if cached_explanation:

            wallet, _ = AIWallet.objects.get_or_create(
                user=request.user
            )

            remaining = (
                max(0, 3 - wallet.free_used)
                if wallet.free_used < 3
                else wallet.paid_credits
            )

            return JsonResponse({
                "status": "success",
                "explanation": cached_explanation,
                "cached": True,
                "cache_type": "semantic",
                "billed": False,
                "remaining": remaining,
                "mode": "cache"
            })

        # =========================
        # 💰 STRICT AI CREDIT SYSTEM
        # =========================
        allowed, mode = use_ai_credit(request.user)

        if not allowed:
            return JsonResponse({
                "status": "upgrade_required",
                "message": "No credits left. Please upgrade.",
                "action": "upgrade"
            }, status=402)

        # =========================
        # 📚 GET USER HISTORY
        # =========================
        history = AIStudyHistory.objects.filter(
            user=request.user
        ).order_by("-created_at")[:10]

        history_text = "\n\n".join(
            f"{h.tool_type.upper()}:\nQ: {h.prompt}\nA: {h.response}"
            for h in history
        )

        # =========================
        # 🔍 SPECIAL CASE
        # =========================
        study_questions = [
            "what did i study",
            "what have i studied",
            "from what we've discussed",
            "what topics have i studied",
            "what have we discussed"
        ]

        if any(q in text.lower() for q in study_questions):

            recent_topics = [h.prompt for h in history]

            topic_html = "".join(
                f"<li>{topic}</li>"
                for topic in recent_topics
            )

            explanation = f"""
            <h2>Your Recent Study Activity</h2>

            <p>
            Based on your recent study history, these are the topics you've been studying:
            </p>

            <ul>
                {topic_html}
            </ul>

            <h3>Summary</h3>

            <p>
            From your recent activity, you appear to be studying academic-related topics,
            general knowledge, and structured learning materials.
            </p>
            """

        else:

            # =========================
            # 🤖 GEMINI PROMPT
            # =========================
            prompt = f"""
You are an expert study tutor.

The user may ask questions about previous discussions.

Previous Study History:
{history_text}

Current Topic:
{text}

Rules:
- Return HTML only
- Use <h2>, <h3>, <p>, <ul><li>
- Maximum 300 words
- Explain like a teacher
- Break complex ideas into simple parts
- Use examples
- Do NOT use markdown
- Use history if relevant

Structure:

<h2>Topic Name</h2>

<h3>Introduction</h3>
<p>...</p>

<h3>Key Concepts</h3>
<ul>
    <li>...</li>
</ul>

<h3>Detailed Explanation</h3>
<p>...</p>

<h3>Examples</h3>
<p>...</p>

<h3>Summary</h3>
<p>...</p>
"""

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            explanation = response.text.strip()

        # =========================
        # 💾 SAVE HISTORY
        # =========================
        AIStudyHistory.objects.create(
            user=request.user,
            tool_type="explain_topic",
            prompt=text,
            response=explanation
        )

        # =========================
        # 🧹 CLEAN OLD HISTORY
        # =========================
        user_history = AIStudyHistory.objects.filter(
            user=request.user
        ).order_by("created_at")

        if user_history.count() > 1000:

            excess = user_history.count() - 1000

            oldest_ids = user_history.values_list(
                "id",
                flat=True
            )[:excess]

            AIStudyHistory.objects.filter(
                id__in=oldest_ids
            ).delete()

        # =========================
        # 💾 SAVE TO EXACT CACHE
        # =========================
        cache.set(
            exact_cache_key,
            explanation,
            timeout=60 * 60
        )

        # =========================
        # 💾 SAVE TO SEMANTIC CACHE
        # =========================
        semantic_cache_set(
            cache_key,
            text,
            explanation
        )

        # =========================
        # 🔥 WALLET STATUS RESPONSE
        # =========================
        wallet, _ = AIWallet.objects.get_or_create(
            user=request.user
        )

        remaining = (
            max(0, 3 - wallet.free_used)
            if mode == "free"
            else wallet.paid_credits
        )

        return JsonResponse({
            "status": "success",
            "explanation": explanation,
            "cached": False,
            "cache_type": None,
            "remaining": remaining,
            "mode": mode
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
        
    
        
@receiver(post_save, sender=User)
def create_ai_wallet(sender, instance, created, **kwargs):
    if created:
        AIWallet.objects.create(user=instance)
        
def use_ai_credit(user):
    wallet, _ = AIWallet.objects.get_or_create(user=user)

    today = date.today()

    # reset daily free usage
    if wallet.last_reset is None or wallet.last_reset < today:
        wallet.free_used = 0
        wallet.last_reset = today
        wallet.save()

    # FREE TIER
    if wallet.free_used < 3:
        wallet.free_used += 1
        wallet.save()
        return True, "free"

    # PAID CREDITS
    if wallet.paid_credits > 0:
        wallet.paid_credits -= 1
        wallet.save()
        return True, "paid"

    return False, "blocked"



def get_usd_to_ngn_rate():
    cached_rate = cache.get("usd_ngn_rate")
    if cached_rate:
        return cached_rate

    url = f"https://v6.exchangerate-api.com/v6/{settings.EXCHANGE_API_KEY}/latest/USD"

    try:
        response = requests.get(url, timeout=5)


        data = response.json()

        if data.get("result") == "success":
            rate = Decimal(str(data["conversion_rates"]["NGN"]))

            cache.set("usd_ngn_rate", rate, timeout=60 * 10)
            return rate

    except Exception as e:
        return None
    
def get_currency(country_code):
    mapping = {
        "NG": "NGN",
        "US": "USD",
        "GB": "GBP",
        "CA": "USD",
        "AU": "USD",
        "DE": "EUR",
        "FR": "EUR",
        "ZA": "ZAR",
        "IN": "INR",
    }

    return mapping.get(country_code, "NGN")


@login_required
def buy_ai_credits(request):

    try:
        data = json.loads(request.body or "{}")

        usd_amount = Decimal(str(data.get("usd", 0)))
        credits = int(data.get("credits", 0))

        # =========================
        # VALIDATION
        # =========================
        if usd_amount <= 0 or credits <= 0:
            return JsonResponse({"error": "Invalid package selected"}, status=400)

        if not request.user.email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # =========================
        # FIXED PACKAGES (ANTI-TAMPER)
        # =========================
        PACKAGES = {
            (1, 10),
            (3, 50),
            (Decimal("7.5"), 150),
        }

        if (float(usd_amount), credits) not in PACKAGES:
            return JsonResponse({"error": "Invalid pricing package"}, status=400)

        # =========================
        # USD → NGN conversion
        # =========================
        rate = get_usd_to_ngn_rate()

        if not rate or rate <= 0:
            rate = Decimal("1500")

        ngn_amount = usd_amount * rate
        amount_kobo = int(ngn_amount * 100)

        # =========================
        # PAYSTACK INIT
        # =========================
        payload = {
            "email": request.user.email,
            "amount": amount_kobo,
            "metadata": {
                "user_id": request.user.id,
                "usd_amount": str(usd_amount),
                "credits": credits
            },
            "callback_url": request.build_absolute_uri("/payment/success/")
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )

        result = response.json()

        if not result.get("status"):
            return JsonResponse({"error": result.get("message")}, status=400)

        return JsonResponse({
            "authorization_url": result["data"]["authorization_url"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
 
@csrf_exempt
def paystack_webhook(request):

    payload = request.body
    signature = request.headers.get("X-Paystack-Signature")

    # 🔒 VERIFY SIGNATURE (ANTI-HACK)
    secret = settings.PAYSTACK_SECRET_KEY.encode()

    hash = hmac.new(secret, payload, hashlib.sha512).hexdigest()

    if hash != signature:
        return JsonResponse({"error": "Invalid signature"}, status=403)

    event = json.loads(payload)

    # 💰 PAYMENT SUCCESS
    if event["event"] == "charge.success":

        metadata = event["data"]["metadata"]

        user_id = metadata["user_id"]
        credits = int(metadata["credits"])

        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)

        wallet, _ = AIWallet.objects.get_or_create(user=user)

        # 🔒 IDEMPOTENCY CHECK (avoid double credit)
        transaction_id = event["data"]["id"]

        if PaidTransaction.objects.filter(tx_id=transaction_id).exists():
            return JsonResponse({"status": "duplicate ignored"})

        # # 💳 ADD CREDITS
        # wallet.paid_credits += credits
        # wallet.save()

        # 🧾 SAVE TRANSACTION LOG
        PaidTransaction.objects.create(
            user=user,
            tx_id=transaction_id,
            credits=credits,
            amount=event["data"]["amount"] / 100
        )

    return JsonResponse({"status": "ignored"})



@login_required
def credits_page(request):

    wallet, _ = AIWallet.objects.get_or_create(
        user=request.user
    )
    today = date.today()

    # First visit ever
    if wallet.last_reset is None:
        wallet.last_reset = today
        wallet.save()

    # New day => reset free usage
    elif wallet.last_reset < today:
        wallet.free_used = 0
        wallet.last_reset = today
        wallet.save()

    return render(request, "credits.html", {
        "wallet": wallet
    })
    

@login_required
def payment_success(request):
    reference = request.GET.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    res = requests.get(url, headers=headers).json()

    wallet, _ = AIWallet.objects.get_or_create(
        user=request.user
    )
    
    free_remaining = max(0, 3 - wallet.free_used)
    if res.get("status") and res.get("data", {}).get("status") == "success":

        metadata = res["data"]["metadata"]
        credits = int(metadata["credits"])

        wallet.paid_credits += credits
        wallet.save()

        wallet.refresh_from_db()
        
        free_remaining = max(0, 3 - wallet.free_used)
    
        
    return render(
        request,
        "payment_success.html",
        {
            "wallet": wallet,
            "reference": reference,
            "free_remaining": free_remaining,
        }
    )
    

def enforce_ai_limit(user):
    allowed, mode = use_ai_credit(user)

    if not allowed:
        return JsonResponse({
            "status": "upgrade_required",
            "message": "You’ve reached your limit. Please upgrade.",
            "action": "upgrade"
        }, status=402), None

    return None, mode

def get_embedding(text):
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="semantic_similarity",
        )

        return np.array(
            result["embedding"],
            dtype=np.float32
        )

    except Exception:
        return None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def semantic_cache_get(cache_key, new_text, threshold=0.92):

    cached_items = cache.get(cache_key, [])

    new_vec = get_embedding(new_text)

    if new_vec is None:
        return None

    for item in cached_items:

        old_vec = np.array(
            item["embedding"],
            dtype=np.float32
        )

        score = cosine_similarity(
            new_vec,
            old_vec
        )

        if score >= threshold:
            return item["response"]

    return None

def semantic_cache_set(cache_key, text, response, max_size=20):

    vec = get_embedding(text)

    if vec is None:
        return

    items = cache.get(cache_key, [])

    items.append({
        "embedding": vec.tolist(),
        "response": response
    })

    if len(items) > max_size:
        items = items[-max_size:]

    cache.set(
        cache_key,
        items,
        timeout=60 * 60
    )
    
# -------------->
@login_required
def verify_transcript(request):
    doc_id = request.GET.get("doc_id")

    gpa_records = GPARecord.objects.filter(user=request.user)

    cgpa_records = CGPARecord.objects.filter(user=request.user)

    profile = StudentProfile.objects.filter(user=request.user).first()

    return render(request, "verify_transcript.html", {
        "doc_id": doc_id,
        "profile": profile,
        "gpa_records": gpa_records,
        "cgpa_records": cgpa_records,
    })

def smart_cell(text):
    text = str(text)

    # only wrap if it's actually long
    if len(text) > 25 or "\n" in text:
        return Paragraph(
            text,
            ParagraphStyle(
                "smart",
                fontSize=9,
                leading=11,
                wordWrap="CJK"
            )
        )

    return text