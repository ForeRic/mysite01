from django.db import models

# Create your models here.
from MySQLdb import connect, OperationalError
from MySQLdb.cursors import DictCursor


def conn():
    return connect(  # db는 객체가 저장 되어있는 주소를 나타냄.
        user='webdb',
        password='webdb',
        host='localhost',
        port=3306,
        db='webdb',
        charset='utf8')

# 리스트를 보기 위함
def findall(page=1, listcount=10):
    try:
        # 연결
        db = conn()

        # cursor 생성
        cursor = db.cursor(DictCursor)
        # db를 보고 결과를 딕셔너리로 줘라. [{'칼럼이름' : '값'}, {'칼럼이름' : '값'}]

        # SQL 실행
        sql = '''
          select no,
	             title,
                 (select name from user where no = board.user_no) as author,
                 user_no,
                 hit,
                 g_no,
                 o_no,
                 depth,
                 reg_date
                 from board
                 order by g_no desc, o_no asc 
                 limit %s, %s'''
        cursor.execute(sql, (page, listcount))
        # 위에서 알려준 sql 쿼리문으로 실행시켜라

        # 결과 받아오기
        results = cursor.fetchall()
        # 모든 데이터를 한꺼번에 클라이언트로 가져올 때 사용 (데이터 베이스에 있는 데이터들을)

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환 ( 출력은 views.py 에서 해줄거니까, 결과값을 반환만 해준다)
        return results

    except OperationalError as e:
        print(f'error: {e}')


def search(kwd):
    try:
        # 연결
        db = conn()

        # cursor 생성:
        # select 되는 특정 집합에 대해서 각 행에 특정 처리 해줄 때 사용.
        # sql 은 보통 칼럼(행) 기반으로 작업. 그러나 row 기반으로 작업하고 싶을 때.
        # where절은 컬럼의 특정 값에 대해 로우(행)을 선택만 함.
        cursor = db.cursor()

        # SQL 실행
        sql = '''
        select no,
                title,
                (select name from user where no = board.user_no) as author,
                hit,
                reg_date
            from board
            where title like concat ('%%', %s, '%%') order by reg_date desc'''
        cursor.execute(sql, (kwd,))

        #결과 받아오기
        results = cursor.fetchall()

        # 자원 정리
        cursor.close() # 커서 오픈했으니 닫아야지
        db.close()  # 데타베이스 오픈했으니 닫아야지

        # 결과 보기
        return results

    except OperationalError as e:
        print(f'error: {e}')


# 게시글 찾기 (읽기위함)
def find(readno):
    try:
        # 연결 및 커서 생성
        db = conn()
        cursor = db.cursor(DictCursor)

        # SQL 실행
        sql = '''
        select  no, 
                title,
                user_no,
                hit,
                contents,
                reg_date,
                g_no,
                o_no,
                depth
        from board 
        where no = %s'''
        cursor.execute(sql, (readno, ))

        # 결과 받아오기
        result = cursor.fetchone()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return result

    except OperationalError as e:
        print(f'error: {e}')


# 글쓰기 작업을 위한 입력 함수
def insert(data):
    try:
        # 연결 및 cursor 생성
        db = conn()
        cursor = db.cursor()

        # SQL 구문 및 커밋
        sql = '''insert into board(
                no, title, contents, user_no, hit, reg_date,
                g_no,
                o_no, depth
            ) values(
                null, %s, %s, %s, 0, now(), 
                ifnull((select max(a.g_no) from board as a),0) + 1,
                0, 0
            )'''
        cnt = cursor.execute(sql, (data['title'], data['contents'], data['user_no']))
        db.commit()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return cnt == 1

    except OperationalError as e:
        print(f'error: {e}')


def update(data):
    try:
        # 연결 및 커서 생성
        db = conn()
        cursor = db.cursor()

        # SQL 실행 및 커밋
        sql = '''update board set
                 title = %s, 
                 contents = %s
            where no = %s
            '''
        ret = cursor.execute(sql, (data['title'], data['contents'], data['no']))
        db.commit()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return ret == 1

    except OperationalError as e:
        print(f'error: {e}')


def delete(delno):
    try:
        # 연결
        db = conn()

        # cursor 생성
        cursor = db.cursor()

        # SQL 실행
        sql = 'delete from board where no = %s'
        cnt = cursor.execute(sql, (delno,))

        # commit
        db.commit()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return cnt == 1

    except OperationalError as e:
        print(f'error: {e}')


def hit(hitno):
    try:
        # 연결
        db = conn()

        # cursor 생성
        cursor = db.cursor()

        # SQL 실행
        sql = 'update board set hit = hit + 1 where no = %s'

        cnt = cursor.execute(sql, (hitno,))

        # commit
        db.commit()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return cnt == 1

    except OperationalError as e:
        print(f'error: {e}')


def reply(data):
    cnt = 0
    try:
        db = conn()

        try:
            # 연관글의 o_no 를 증가
            cursor = db.cursor()
            sql = '''
                update board set o_no = o_no + 1 where g_no = %s and o_no >= %s
            '''
            cnt = cursor.execute(sql, (data['g_no'], data['o_no']))

            # 답변글 Insert
            cursor = db.cursor()
            sql = '''insert into board(
                    no, title, contents, user_no, hit, reg_date, 
                    g_no, o_no, depth
                ) values(
                    null, %s, %s, %s, 0, now(),
                    %s, %s, %s 
                )'''
            cnt = cursor.execute(sql, (data['title'], data['contents'], data['user_no'],
                                          data['g_no'], data['o_no'], data['depth']))

            db.commit()
            cursor.close()

        except Exception as e:
            print(f'error: {e}')
            db.rollback()

        db.close()

        # 결과 반환
        return cnt == 1

    except OperationalError as e:
        print(f'error: {e}')


def count():
    try:
        # 연결 및 커서 생성
        db = conn()
        cursor = db.cursor(DictCursor)

        # SQL 실행
        sql = 'select count(*) as count from board'
        cursor.execute(sql)

        # 결과 받아오기
        result = cursor.fetchone()

        # 자원 정리
        cursor.close()
        db.close()

        # 결과 반환
        return result['count']

    except OperationalError as e:
        print(f'error: {e}')
