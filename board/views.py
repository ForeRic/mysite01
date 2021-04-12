from django.http import HttpResponseRedirect
from django.shortcuts import render
from board import models

LIST_COUNT = 10


def index(request):
    results = models.boardlist()
    data = {'post_list': results}

    page = request.GET.get('p')
    page = 1 if page is None else int(page)

    print(page)

    '''
    page = request.GET['p']
    totalcount = models.count()
    boardlist = models.findall(page, LIST_COUNT)
    # paging 정보 계산
    pagecount = ceil(totalcount / LIST_COUNT)
    data = {
        "boardlist": boardlist,
        "pagecount": pagecount,
        "netpage": 7,
        "prvpage": 5,
        "curpage": 2,
    }
    '''
    return render(request, 'board/index.html', data)


def view(request):
    no = request.GET['no']
    result = models.listbyno(no)
    data = {'result': result}
    return render(request, 'board/view.html', data)


def writeform(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    return render(request, 'board/writeform.html')


def write(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    user_no = authuser['no']
    title = request.POST['title']
    contents = request.POST['content']
    models.insert_post(title, contents, user_no)
    return HttpResponseRedirect('/board')


def updateform(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    no = request.GET['no']
    result = models.listbyno(no)
    if result['bno'] != authuser['no']:
        return HttpResponseRedirect('/')

    data = {'result': result}
    return render(request, 'board/updateform.html', data)


def update(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    ano = request.POST['post_id']
    result = models.listbyno(ano)

    if result['bno'] != authuser['no']:
        return HttpResponseRedirect('/')

    title = request.POST['title']
    contents = request.POST['contents']

    models.update(ano, title, contents)
    return HttpResponseRedirect(f'/board/view?no={ano}')


def deleteform(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    no = request.GET['no']
    result = models.listbyno(no)
    if result['bno'] is not authuser['no']:
        return HttpResponseRedirect('/')

    return render(request, 'board/deleteform.html')


def delete(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    no = request.POST['post_id']
    result = models.listbyno(no)
    if result['bno'] != authuser['no']:
        return HttpResponseRedirect('/')

    password = request.POST['password']
    user_id = models.findby_no_and_ps(no, password)
    if user_id is None:
        return HttpResponseRedirect(f'/board/deleteform?no={no}&result=fail')

    models.deletebyno(no)

    return HttpResponseRedirect('/board')


def replyform(request):
    authuser = request.session.get('authuser')  # 로그인이 안된 상태에서의 접근인지 확인.
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    return render(request, 'board/replyform.html')


def reply(request):
    authuser = request.session.get('authuser')  # 로그인이 안된 상태에서의 접근인지 확인.
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    user_no = authuser['no']  # 'no' = user_no
    ano = request.POST['post_id']
    result = models.listbyno(ano)
    title = request.POST['title']
    contents = request.POST['content']
    g_no = result['g_no']
    depth = result['depth'] + 1
    models.insert_reply(title, contents, g_no, depth, user_no)
    return HttpResponseRedirect('/board')




'''
# 참조 + 참조 및 짜집기..(글목록 안보임.. 서버는 잘 돌아감..) --> 참조 + 분석및 공부용
from math import ceil

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from board import models

# views.py 는 화면에 뿌려주는 역할을 하는 함수를 구현 하는 곳. 실제로 여기서 함수구현을 해야지만, 화면에 보임.

# 생각의 방향:
# 1. 화면에 어떤것이 출력되야하는지 생각.
# 2. 화면 출력을 위해 어떤 함수들이 필요한지 생각.
# 3. 동시다발적으로 models.py 가서 views.py 함수를 구현하기 위한 sql를 포함한 함수를 구현 (데이터를 받아오는 곳)
# 4. views.py 에서 구현된 함수를 보이게 하려면 urls.py 가서 path 를 걸어줘야 함.

LIST_COUNT = 10


# 글 목록(index) 보기 (게시판에서)
def index(request):
    page = request.GET.get('p')  # str.
    # request.GET = 전달받은 것들을 모두 딕셔너리 형태로 가져 오는 것
    # request.GET.get() = 괄호안에 key 입력시 value 가져옴.
    # print(type(page)) # str이라고 나옴 terminal 에
    page = 1 if page is None else int(page)  # int 로 바꾸는 작업

    # totalcount = models.count()
    # boardlist = models.findall(page, LIST_COUNT)
    # pagecount = ceil(totalcount / LIST_COUNT)

    # paging 정보를 계산
    # data = {
    #    "boardlist": boardlist,
    #    'pagecount': pagecount,
    #     'nextpage': 7,
    #   'prepage': 5,
    #   ' curpage': 2
    # }

    # select * from board limit 0, 10
    # select * from board limit 10, 20

    indx = (page - 1) * LIST_COUNT
    results = models.findall(indx, LIST_COUNT)

    totalcount = models.count()  # 전체 게시글 갯수 세는 작업
    pagecount = ceil(totalcount / LIST_COUNT)
    # ceil : 무조건 올림. (반올림 반내림 따위 하지 않음)
    # 예) 33개 게시물/10개씩 보여줘라: 페이지 3.3페이지 이므로 총 페이지 4개 나오도록 몫을 3이 아닌 4가 되게 함.
    curpage = page
    nextpage = curpage + 1 if curpage < pagecount else curpage
    prvpage = 1 if (curpage - 1) < 1 else (curpage - 1)

    # 게시판에서 페이지당 몇개의 글을 보여줄지 정하는 모듈
    paginator = {
        'pagecount': pagecount,
        'nextpage': nextpage,
        'prevpage': prvpage,
        'curpage': curpage,
        'paging': range(1, 6)
    }

    data = {
        'boardlist': results,
        'kwd': '',
        'paginator': paginator
    }

    return render(request, 'board/index.html', data)


# 게시글을 읽읍시다
def view(request):
    viewno = request.GET.get('no')
    if viewno is None:
        return HttpResponse('Access Denied')

    result = models.find(viewno)
    if result is None:
        return HttpResponse('Nothing to show!')

    data = {'post': result}

    # hit 증가시키기 (조회수)
    models.hit(viewno)
    return render(request, 'board/view.html', data)


# 글 쓰기
def writeform(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        # 유저가 없거나 세션해제. --> 유저의 로긴form으로 가셈
        return HttpResponseRedirect('/user/loginform')

    return render(request, 'board/writeform.html')


# wirteform.html 에서 할 액션.
def write(request):
    authuser = request.session.get('authuser')
    if authuser is None:
        return HttpResponseRedirect('/user/loginform')

    title = request.POST.get('title', '')
    contents = request.POST.get('contents', '')

    # request.POST = request 의 POST 값들을 딕셔너리 형태로 반환. 키 값이 존재 안하면 키에러.
    # request.POST.get() = 특정 키 값의 값 반환. 존재하지 않는 키는 none 으로 반환. 키 값이 없으면 .get('key', 'defalutvalue') 로 설정 가능.

    # 정보를 데이타 딕셔너리에 저장합시다. ()에 값을 넣어주기 위해.
    data = {
        'user_no': authuser['no'],
        'title': title,
        'contents': contents
    }
    # 글쓰기 작업을 위한 입력 함수 델꼬옴.
    result = models.insert(data)  # models.insert(data) 하면 어떤 값이 튀어나옴 => 그걸 result로 받는다
    if result != 1:  # 입력을 했으면 값이 최소 1이어야 하는데 1이 아니라면 에러가 나야 하니까!
        return HttpResponse('error')

    return HttpResponseRedirect('/board')
    # return HttpResponseRedirect('/board/view?no=')


# 글을 수정하기 위한 updateform.html이 할 행동.
def updateform(request):
    authuser = request.session.get('authuser')
    if authuser is None:  # 만약 너가 유저가 아니라면, 다시 로긴하러 가랏.
        return HttpResponseRedirect('/user/loginform')

    upformno = request.GET.get('no')
    if upformno is None:
        return HttpResponse('Wrong Access!')
    result = models.find(upformno)
    if result is None:
        return HttpResponse('Noting to show')

    if result['user_no'] != authuser['no']:
        return HttpResponse('Oops! You are not authorized!')

    data = {'post': result}
    return render(request, 'board/updateform.html', data)


#updateform.html 이 해야할 행동: 변경!!
def update(request):
    authuser = request.session.get('authuser')
    if authuser is None:  # 만약 너가 유저가 아니라면, 다시 로긴하러 가랏.
        return HttpResponseRedirect('/user/loginform')

    updateno = request.GET.get('no')
    if updateno is None:
        return HttpResponse('Wrong Access!')
    result = models.find(updateno)
    if result is None:
        return HttpResponse('Noting to show')

    if result['user_no'] != authuser['no']:
        return HttpResponse('Oops! You are not authorized!')

    title = request.POST.get('title','')
    contents = request.POST.get('contents', '')

    data = {
        'title': title,
        'contents': contents,
        'no': updateno
    }
    models.update(data)
    return HttpResponseRedirect('/board')


# 글 삭제
def delete(request):
    authuser = request.session.get('authuser')
    if authuser is None:  # 만약 너가 유저가 아니라면, 다시 로긴하러 가랏.
        return HttpResponseRedirect('/user/loginform')

    delno = request.GET.get('no')
    if delno is None:
        return HttpResponse('Wrong Access!')
    result = models.find(delno)
    if result is None:
        return HttpResponse('Noting to show')

    if result['user_no'] != authuser['no']:
        return HttpResponse('Oops! You are not authorized!')

    models.delete(delno)
    return HttpResponseRedirect('/board')

# 답글 처리

def replyform(request):
    authuser = request.session.get('authuser')
    if authuser is None:  # 만약 너가 유저가 아니라면, 다시 로긴하러 가랏.
        return HttpResponseRedirect('/user/loginform')

    readno = request.GET.get('no')
    if readno is None:
        return HttpResponse('Wrong Access!')
    result = models.find(readno)
    if result is None:
        return HttpResponse('Noting to show')

    data = {'reply': result}
    return render(request, 'board/replyform.html', data)


def reply(request):
    authuser = request.session.get('authuser')
    if authuser is None:  # 만약 너가 유저가 아니라면, 다시 로긴하러 가랏.
        return HttpResponseRedirect('/user/loginform')

    title = request.POST.get('title', '')
    contents = request.POST.get('contents', '')
    g_no = request.POST.get('g_no', 0)
    o_no = request.POST.get('o_no', 0)
    depth = request.POST.get('depth', 0)

    g_no = int(g_no)
    o_no = int(o_no) + 1
    depth = int(depth) + 1

    # 받아온 데이터 저장 딕셔너리로 저장
    data = {
        'user_no': authuser['no'],
        'title': title,
        'contents': contents,
        'g_no': g_no,
        'o_no': o_no,
        'depth': depth
    }

    rst = models.reply(data)
    if rst !=1:
        return HttpResponse('Error')

    return HttpResponseRedirect('/board')
'''

'''
from math import ceil

from django.http import HttpResponseRedirect
from django.shortcuts import render

from board import models

LIST_COUNT = 10


def index(request):
   # page = request.GET.get("p")
    #page = 1 if page is None else int(page)

    #print(page)

    # totalcount = models.count()
    # boardlist = models.findall(page, LIST_COUNT)

    # paging 정보를 계산
    # pagecount = ceil(totalcount / LIST_COUNT)
    #
    # data = {
    #     "boardlist": boardlist,
    #     'pagecount': pagecount,
    #     'netpage': 7,
    #     'prvpage': 5,
    #     'curpage': 2
    #
    # }

    #indx = (page - 1) * LIST_COUNT

    '
    totalcount = models.count()  # 전체 게시글 갯수 세는 작업
    pagecount = ceil( totalcount / LIST_COUNT)
    # ceil : 무조건 올림. (반올림 반내림 따위 하지 않음)
    # 예) 33개 게시물/10개씩 보여줘라: 페이지 3.3페이지 이므로 총 페이지 4개 나오도록 몫을 3이 아닌 4가 되게 함.
    curpage = page
    nextpage = curpage + 1 if curpage < pagecount else curpage
    prvpage = 1 if (curpage - 1) < 1 else (curpage - 1)

    # 게시판에서 페이지당 몇개의 글을 보여줄지 정하는 모듈
    paginator = {
        'pagecount': pagecount,
        'nextpage': nextpage,
        'prevpage': prvpage,
        'curpage': curpage,
        'paging': range(1, 6)
    }
    '
    results = models.boardlist()
    data = {'boardlist': results}

    return render(request, 'board/index.html', data)


def view(request):

    boardno = request.GET["no"]
    oneboard = models.getboard(boardno)
    data = {'oneboard': oneboard}
    return render(request, 'board/view.html', data)


def writeform(request):
    return render(request, 'board/writeform.html')

def write(request):

    title = request.POST["title"]
    content = request.POST["content"]
    userno = request.session["authuser"]["no"]
    models.insert(title, content, userno)

    return HttpResponseRedirect('/board')


def updateform(request):

    boardno = request.GET["no"]
    oneboard = models.getboard(boardno)
    data = {"oneBoard": oneboard}

    return render(request, 'board/updateform.html', data)


def update(request):

    boardno = request.POST["boardno"]
    title = request.POST["title"]
    content = request.POST["content"]
    models.update(title, content, boardno)

    return HttpResponseRedirect(f'/board/view?no={boardno}')


def delete(request):

    boardno = request.GET["no"]
    models.delete(boardno)

    return HttpResponseRedirect('/board')


def replyform(request):
    return render(request, 'board/replyform.html')


def reply(request):

    originalboardno = request.POST["originalboardno"]
    originalboard = models.getboard(originalboardno)
    original_g_no = originalboard["g_no"]
    original_o_no = originalboard["o_no"]
    originaldepth = originalboard["depth"]
    models.updatereply(original_g_no, original_o_no)

    title = request.POST["title"]
    content = request.POST["content"]
    userno = request.session["authuser"]["no"]
    models.insertreply(title, content, original_g_no, original_o_no, originaldepth, userno)

    return HttpResponseRedirect('/board')


def search(request):

    keyword = request.POST["kwd"]
    boardserach = models.search(keyword)
    data = {'boardlist': boardserach}

    return render(request, 'board/index.html', data)

'''

