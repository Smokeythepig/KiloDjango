from django.shortcuts import render
from .models import Skill
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'skillsswap/skill_list.html', {'skills': skills})


@login_required
def dashboard(request):
    skills = Skill.objects.all()

    category_filter = request.GET.get('category')

    if category_filter:
        skills = skills.filter(category=category_filter)

    total_skills = skills.count()

    category_totals = skills.values('category').annotate(count=Count('category'))

    return render(request, 'skillsswap/dashboard.html', {
        'total_skills': total_skills,
        'category_totals': category_totals
    })