from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Recommendation_Posts)
admin.site.register(Reels)
admin.site.register(ReelLike)
admin.site.register(ReelComment)
admin.site.register(Recommendation_Reels)