from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Design, Category, SubCategory

# Create your views here.

@login_required
def gallery(request):
    designs = Design.objects.all()
    categories = Category.objects.all()
    
    # Apply filters
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_id:
        designs = designs.filter(category_id=category_id)
    
    if search_query:
        designs = designs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Store gallery session data
    request.session['last_visited_gallery'] = True
    request.session['last_gallery_visit'] = str(request.user.id)
    
    return render(request, 'gallery/gallery.html', {
        'designs': designs, 
        'categories': categories
    })

@login_required
def design_detail(request, design_id):
    design = get_object_or_404(Design, id=design_id)
    
    # Store design detail session data
    request.session['last_viewed_design'] = design_id
    request.session['last_viewed_design_name'] = design.name
    
    return render(request, 'gallery/design_detail.html', {'design': design})