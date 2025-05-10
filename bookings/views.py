from django.shortcuts import render

def pricing_page(request):
    return render(request, 'subscription/subscriptions_list.html', {'title': 'Pricing Plans'})