from django.http import HttpResponseRedirect
from django.shortcuts import render

import guestbook.models as guestbookmodel

def index(request):
    results = guestbookmodel.findall()
    data = {'guestbooklist': results}
    return render(request, 'guestbook/index.html', data)

def deleteform(request):
    return render(request, 'guestbook/deleteform.html')

def add(request):
    name = request.POST['name']
    password = request.POST['password']
    content = request.POST['content']

    guestbookmodel.insert(name, password, content)

    return HttpResponseRedirect('/guestbook')

def delete(request):
    no = request.POST['no']
    password = request.POST['password']

    guestbookmodel.deleteby_no_and_password(no, password)

    return HttpResponseRedirect('/guestbook')