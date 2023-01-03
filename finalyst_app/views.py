from django.shortcuts import get_object_or_404, render, redirect
from .models import *
##################################################
## Uncomment if you want to apply the AI model ###
##################################################
# from .apps import FinalystAppConfig

def home(request):
    if (request.method == 'POST'):
        new_search = Search()
        new_search.keyword = request.POST['keyword']
        new_search.save()
        return redirect('result', new_search.keyword)
    return render(request, 'home.html')

def result(request, kw):
    search = get_object_or_404(Company, title = kw)
    ##################################################
    ## Uncomment if you want to apply the AI model ###
    ##################################################
    # a, b = FinalystAppConfig.generator.inference()
    # search.result_pos = a['topic_info']
    # search.result_neg = b['topic_info']
    # search.save()
    ctx = {
        'search':search,
    }
    return render(request, 'result.html', ctx)
