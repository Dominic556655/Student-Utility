from django.contrib import admin
from .models import Post
from .models import Comment
from .models import CGPARecord
from .models import GPARecord
from .models import ExamHistory
from .models import Assignment
from .models import Course
from .models import TimetableEntry
from .models import StudySession
from .models import AIStudyHistory
from .models import AIUsage
from .models import AIWallet
from .models import PaidTransaction
from .models import AISemanticCache

# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(CGPARecord)
admin.site.register(GPARecord)
admin.site.register(ExamHistory)
admin.site.register(Assignment)
admin.site.register(Course)
admin.site.register(TimetableEntry)
admin.site.register(StudySession)
admin.site.register(AIStudyHistory)
admin.site.register(AIUsage)
admin.site.register(AIWallet)
admin.site.register(PaidTransaction)
admin.site.register(AISemanticCache)