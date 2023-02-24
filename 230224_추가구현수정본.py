# 트리거 생성은 heidisql에서

# cart 트리거 생성 쿼리문!
# DELIMITER //
# CREATE TRIGGER max_rows_trigger
# BEFORE INSERT ON cart
# FOR EACH ROW
# BEGIN
#   DECLARE num_rows INT;
#   SELECT COUNT(*) INTO num_rows FROM cart;
#   IF num_rows >= 5 THEN
#     SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maximum number of rows reached';
#   END IF;
# END //
# DELIMITER ;

# rent_list 트리거 생성 쿼리문
# DELIMITER //
# CREATE TRIGGER update_borrow
# AFTER DELETE ON rent_list
# FOR EACH ROW
# BEGIN
# UPDATE book_list SET borrow ='Y'
# WHERE book_num = OLD.book_num;
# END //
# DELIMITER ;

import pymysql
from time import localtime, strftime
import unicodedata  # 한글이 포함된 문자열에 간격 맞추기 솔루션을 제공하는 라이브러리

# import unicodedata  # 한글이 포함된 문자열에 간격 맞추기 솔루션을 제공하는 라이브러리
# from wcwidth import wcswidth  # 한글이 포함된 문자열에 간격 맞추기 솔루션을 제공하는 라이브러리
#
#
# def preFormat(string, width, align='<', fill=' '):
#     count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in string))
#     return {
#         '>': lambda s: fill * count + s,  # lambda 매개변수 : 표현식
#         '<': lambda s: s + fill * count,
#         '^': lambda s: fill * (count / 2)
#                        + s
#                        + fill * (count / 2 + count % 2)
#     }[align](string)
#
#
# def fmt(x, w, align='r'):  # align의 기본값은 'r : right'
#     """ 동아시아문자 폭을 고려하여, 문자열 포매팅을 해 주는 함수.
#     w 는 해당 문자열과 스페이스문자가 차지하는 너비.
#     align 은 문자열의 수평방향 정렬 좌/우/중간.
#     """
#     x = str(x)  # 해당 문자열
#     l = wcswidth(x)  # 문자열이 몇자리를 차지하는지를 계산.
#     s = w - l  # 남은 너비 = 사용자가 지정한 전체 너비 - 문자열이 차지하는 너비
#     if s <= 0:
#         return x
#     if align == 'l':
#         return x + ' ' * s
#     if align == 'c':
#         sl = s // 2  # 변수 좌측
#         sr = s - sl  # 변수 우측
#         return ' ' * sl + x + ' ' * sr
#     return ' ' * s + x


num = 0
promt = """
===========================================
 어서오세요. 광산구 도서관 도서관리 프로그램입니다
===========================================
         원하시는 번호를 눌러주세요
              1. 회원가입
              2. 로그인
              3. 종료
===========================================
입력: """

cust_info = []
check_result = []
cart_id = 1
rent_id = 1


def return_rent():  # 도서 반납 함수
    check_num = 0
    print("[ 도서 반납하기 ]")

    # rent_list 출력하기
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    # SUBSTR(book_name, 1, 30) as sub_bk_name,
    # SUBSTR(author, 1, 30) as sub_bk_author,

    sql = '''    
        SELECT rent_id,
               book_num,
               lib_name, 
               book_name,
               author,
               rent_date, return_date
        FROM rent_list
        ORDER BY rent_date
        '''
    cursor.execute(sql)
    result = cursor.fetchall()

    # rent_list에 데이터가 0개일 때
    if result == ():
        print("반납할 도서가 없습니다.")
        return

    print('(등록번호, 소장도서관, 책이름, 지은이, 출판사, 대여가능여부)')

    for i in range(len(result)):
        print(result[i], end='\n')

    # strFormat = '%-10s%-20s%-20s%-10s%-10s%-10s%-10s\n'
    # strOut = strFormat % (
    # preFormat('대여번호', 0), preFormat('등록번호', 0), preFormat('도서관명', 0), preFormat('도서명', 50), preFormat('저자', 45)
    # , preFormat('대여일', 20), preFormat('반납일', 20))
    #
    # for i in range(len(result)):
    #     strOut += strFormat % (preFormat(str(result[i][0]), 0), preFormat(result[i][1], 0), preFormat(result[i][2], 0),
    #                            preFormat(result[i][3], 60), preFormat(result[i][4], 50),
    #                            preFormat(result[i][5].strftime("%Y-%m-%d"), 20),
    #                            preFormat(result[i][6].strftime("%Y-%m-%d"), 0))
    #
    # # 최종 출력
    # return print(strOut)
    #
    # for i in range(len(result)):
    #     print('{} {} {} {} {} {} {}'.format(preFormat(str(result[i][0]),7), preFormat(result[i][1], 20), preFormat(result[i][2], 20), preFormat(result[i][3], 20)
    #     ,preFormat(result[i][4], 50), preFormat(result[i][5].strftime("%Y-%m-%d"), 10), preFormat(result[i][6].strftime("%Y-%m-%d"), 10)))
    # #     # print(result[i], end='\n')

    user_id = input("반납할 도서의 등록번호를 입력하세요: ")

    for i in range(len(result)):
        if user_id == result[i][1]:
            check_num = 1

    if check_num == 1:
        sql2 = '''
                DELETE FROM rent_list 
                WHERE book_num = %s
                '''
        cursor.execute(sql2, (user_id))  # result[0] = book_num
        conn.commit()

        # book_list의 borrow열을 Y으로 바꿔주기(대여 가능하도록)
        sql3 = '''
            UPDATE book_list SET
            borrow = %s WHERE book_num = %s
            '''
        print(f"등록번호 : {result[0][1]}, 도서명 : {result[0][3]} 을 반납하였습니다. ")

        cursor.execute(sql3, ('Y', (user_id)))
        conn.commit()
    else:
        print("대여 목록에 없는 등록번호 입니다.")

    cursor.close()
    conn.close()


def book_rent(check_result):  # 장바구니에 있는 목록 출력 후 대여여부 선택하기
    # 매개변수 check_result는 현재 로그인된 cust의 정보가 담겨 있음(check_ID(), check_PWD()함수 참고)
    global rent_id

    cart_check = print_cart()  # 장바구니 목록 출력해주는 함수 호출
    if cart_check == -1:
        return

    input_bookid = input("대여할 도서의 등록번호를 입력하세요: ")

    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()


    count_sql = f'''
                SELECT cust_id, count(*) as count
                FROM rent_list
                WHERE rent_list.cust_id like ('{(check_result[0])}')
                GROUP BY cust_id
               '''
    cursor.execute(count_sql)
    count_result = cursor.fetchall()
    # print(test_result)

    # cust_id별로 5권 이상 대여할 수 없도록 하는 기능 구현
    # 대여목록이 0개 ~ 5개까지일 때 작동함
    if count_result == () or count_result[0][1] <= 4:

        # rent_list에 데이터 넣기 위해서 book_list에서 가져올 수 있는 col명들 select
        sql = '''    
                SELECT book_num, lib_name, book_name, author, publisher, borrow
                FROM book_list
                WHERE book_num LIKE CONCAT(%s)
                '''
        cursor.execute(sql, (input_bookid))
        result = cursor.fetchone()

        # rent_id 길이 구하기
        sql2 = '''    
                SELECT rent_id
                FROM rent_list
                '''
        cursor.execute(sql2)
        rent_id = len(cursor.fetchall()) + 1
        # print(rent_id)

        try:

            sql3 = '''
                    INSERT INTO rent_list (rent_id, book_num, lib_name, book_name, cust_id,
                    author, publisher, rent_date, return_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY))
                    '''

            cursor.execute(sql3, (rent_id, result[0], result[1], result[2], check_result[0],
                                  result[3], result[4]))
            conn.commit()

            # rent_list에 대여내용 넣었다면 book_list의 borrow열을 N으로 바꿔주기(대여 불가능하도록)
            sql4 = '''
                        UPDATE book_list SET
                        borrow = %s WHERE book_num = %s
                        '''
            cursor.execute(sql4, ('N', (input_bookid)))
            conn.commit()

            # cart에서 삭제하기
            sql5 = '''
                       DELETE FROM cart 
                       WHERE book_num = %s
                        '''
            cursor.execute(sql5, (result[0]))  # result[0] = book_num
            conn.commit()

        except Exception as err:
            if err.args[0] == 1062:
                print("이미 대여한 등록번호입니다. 다른 책을 대여해주세요.")
            else:
                print("해당 등록번호를 찾을 수 없습니다.")

        finally:
            conn.commit()
            cursor.close()
            conn.close()
    else:
        print("1인당 대여가능한 권수(5권)를 초과하였습니다.")


def print_cart():  # 장바구니 테이블(cart)을 출력해주는 함수
    conn = pymysql.connect(  # DB 연결
        host='127.0.0.1', user='root', password='123456',
        db='book_management', charset='utf8')
    cursor = conn.cursor()

    sql = '''
          SELECT *
          FROM cart
          '''
    cursor.execute(sql)
    result = cursor.fetchall()

    print(f"[ 장바구니 ]")

    if result == ():
        print("장바구니에 담긴 도서가 없습니다.")
        return -1

    for i in range(len(result)):
        print(result[i], end='\n')

    cursor.close()
    conn.close()


def print_rent():  # 도서를 대여하는 함수 호출         ##
    try:

        rent_user_num = 0

        while rent_user_num != 3:
            print("-----------------------------")
            print("     [ 도서대여 ]")
            print("")
            print("     1. 대여하기")
            print("     2. 뒤로가기")
            print("")
            print("-----------------------------")

            rent_user_num = int(input("입력: "))

            if rent_user_num == 1:
                book_rent(check_result)
            elif rent_user_num == 2:
                print("메인화면으로 돌아갑니다.")
                return

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')

    else:
        print("잘못된 입력입니다. 1~2의 숫자를 입력해주세요.")



def print_search():
    try:
        while True:

            print("-----------------------------")
            print("      「 소장자료 검색 」")
            print("     1. 도서명으로 검색")
            print("     2. 저자명으로 검색")
            print("     3. 장바구니 담기\n        (등록번호 입력)")
            print("     4. 뒤로가기")
            print("-----------------------------")
            book_list_num = int(input("입력: "))

            if book_list_num == 1:  ##도서명으로 검색

                conn = pymysql.connect(  # DB 연결
                    host='127.0.0.1', user='root', password='123456',
                    db='book_management', charset='utf8')
                cursor = conn.cursor()

                print("도서명검색을 선택하였습니다. (도서를 찾으셨으면, 초기화면의 3번으로 가서 조회하세요)")

                input_book_name = input("도서명을 입력하세요: ")

                sql = '''
                    SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow 
                    FROM book_list 
                    WHERE book_name
                    LIKE CONCAT('%%', %s, '%%')
                    '''
                cursor.execute(sql, (input_book_name,))  # 위의 sql 구문을 실행하기

                result = cursor.fetchall()

                if result == ():
                    print("해당 도서명을 찾을 수 없습니다.")
                    continue

                print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')

                for i in range(len(result)):
                    print(result[i], end='\n')

                cursor.close()
                conn.close()


            elif book_list_num == 2:  ##저자명 검색

                conn = pymysql.connect(  # DB 연결

                    host='127.0.0.1', user='root', password='123456',

                    db='book_management', charset='utf8')

                cursor = conn.cursor()

                print("저자명검색을 선택하였습니다.(도서를 찾으셨으면, 초기화면의 3번으로 가서 조회하세요)")

                input_author = input("저자명을 입력하세요: ")

                sql = '''
                        SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow
                        FROM book_list
                        WHERE author 
                        LIKE CONCAT('%%', %s, '%%')
                        '''

                cursor.execute(sql, (input_author,))  # 위의 sql 구문을 실행하기
                result = cursor.fetchall()

                if result == ():
                    print("해당 저자명을 찾을 수 없습니다.")
                    continue

                print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')
                for i in range(len(result)):
                    print(result[i], end='\n')

                cursor.close()
                conn.close()


            elif book_list_num == 3:  ##등록번호로 검색

                conn = pymysql.connect(  # DB 연결

                    host='127.0.0.1', user='root', password='123456',

                    db='book_management', charset='utf8')

                cursor = conn.cursor()

                print("등록번호검색을 선택하였습니다.")

                input_author = input("등록번호를 입력하세요: ")

                sql = '''
                         SELECT book_id, lib_name, ref_lib, book_num, book_name, author, publisher, borrow 
                         FROM book_list 
                         WHERE book_num 
                         LIKE CONCAT(%s)
                         '''

                cursor.execute(sql, (input_author))  # 위의 sql 구문을 실행하기

                result = cursor.fetchall()

                if result == ():
                    print("해당 등록번호를 찾을 수 없습니다.")
                    continue

                cursor.close()
                conn.close()

                print('(연번, 소장도서관, 자료실명, 등록번호, 책이름, 지은이, 출판사, 대여가능여부)')
                print(result)

                cart = input("장바구니에 넣겠습니까? 1.예 2.아니요 : ")

                # print(result[0][7])
                if result[0][7] == 'N':
                    print("현재 대여중인 도서입니다.")
                    return

                if int(cart) == 1:  # borrow가 Y일 때만 카트에 담을 수 있음. 대여 중인데 또 카트에 넣어지는 에러해결
                    try:
                        conn = pymysql.connect(
                            host='127.0.0.1', user='root', password='123456',
                            db='book_management', charset='utf8'
                        )
                        cursor = conn.cursor()
                        sql = '''
                            INSERT INTO cart (book_num, book_name, author, cust_id)
                            VALUES (%s,%s,%s,%s)
                            '''
                        print(result)

                        cursor.execute(sql, (result[0][3], result[0][4], result[0][5], check_result[0]))


                    except Exception as err:
                        if err.args[0] == 1062:
                            print("중복된 등록번호입니다. 다른 책을 장바구니에 넣어주세요")
                        if err.args[0] == 1644:
                            print("대여 가능한 권수를 초과하였습니다. (1인 최대 5권 대여 가능)")
                        # else:
                        #     print(err)
                        continue

                    finally:
                        conn.commit()
                        cursor.close()
                        conn.close()
                else:
                    continue


            elif book_list_num == 4:
                print("메인메뉴로 돌아가기")
                break

            else:
                print('잘못 입력하였습니다. 1~4사이의 수를 입력하세요')

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')

    else:
        if num == 4:
            print("뒤로 돌아갑니다.")
            return

def print_main():  # 메인 메뉴 출력 함수
    try:
        main_user_num = 0

        while main_user_num != 5:

            print("원하시는 메뉴를 선택하세요")
            print("-----------------------------")
            print("      도서 메뉴")
            print("     1. 도서조회")
            print("     2. 도서대여")
            print("     3. 도서반납")
            print("     4. 장바구니")
            print("     5. 뒤로가기")
            print("-----------------------------")

            main_user_num = int(input("입력: "))

            if main_user_num == 1:
                print("도서조회를 선택하였습니다")
                print_search()  # 도서조회 메뉴 출력 함수 호출
            elif main_user_num == 2:
                print("도서대여를 선택하였습니다")
                print_rent()
            elif main_user_num == 3:
                print("도서반납을 선택하였습니다")
                return_rent()
            elif main_user_num == 4:
                print("장바구니를 확인합니다")
                print_cart()
            else:
                print("잘못된 입력입니다. 1~5의 숫자를 입력해주세요.")
    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 로그아웃 되었습니다.')

    else:
        if num == 5:
            print("로그아웃 되었습니다.")
            return


def check_PWD(input_id, input_pwd, check_result):  # 비밀번호 일치여부를 확인하는 함수 (매개변수로는 사용자가 입력한 id, pw, check_id()의 리턴값)
    if check_result[0] == input_id and check_result[1] == input_pwd:
        print("로그인 되었습니다.")
        print_main()  # 로그인 성공시 메인 메뉴 출력
        return check_result
    else:
        print(f"아이디 또는 비밀번호가 일치하지 않습니다.")


def check_ID(input_id):  # 사용자에게 입력받은 input_id가 DB에 있는지 확인하는 함수
    global check_result
    check = 0  # 무한루프 돌리기 위해 설정함

    while check != 1:

        conn = pymysql.connect(  # DB 연결
            host='127.0.0.1', user='root', password='123456',
            db='book_management', charset='utf8')
        cursor = conn.cursor()

        # member_info 테이블 전체 불러오기 => 아이디, 비밀번호 둘 다 필요하기 때문에.
        sql = '''
        SELECT * FROM member_info
        '''
        cursor.execute(sql)  # 위의 sql 구문을 실행하기
        result = cursor.fetchall()  # 쿼리문의 출력결과를 모두 가져와서 result에 넣기(타입은 튜플임)

        for i in range(len(result)):  # 전체 데이터 중에서 사용자가 입력한 input_id와 일치하는 id가 있는지 찾기
            check_result = result[i]  # 만약 일치하는 id가 있다면 해당하는 행(row)의 정보를 저장하기 위함
            if result[i][0] == input_id:
                check = 1
                cursor.close()
                conn.close()
                return check_result  # 일치하는 정보의 DB행을 return 값으로 반환함

        if check == 0:
            print(f"존재하지 않는 아이디입니다.")
            cursor.close()
            conn.close()
            return -1


def account_login():  # 계정 로그인을 위한 함수
    print("[ 로그인 ]")
    print(f"id를 입력하세요 : ")
    input_id = input()  # user에게 id 입력받음
    print(f"pw를 입력하세요 : ")
    input_pwd = input()  # user에게 pwd 입력받음

    return_id = check_ID(input_id)  # user가 입력한 id가 DB에 있는지 확인하는 함수 호출한 후 return값(있으면 행(row)정보, 없으면 -1)을 return_id에 저장
    # print(f"id_check : {return_id}")
    if return_id != -1:  # return 값이 -1이 아닐 때 (즉, id가 존재할 때)
        check_PWD(input_id, input_pwd, return_id)  # user가 입력한 비밀번호가 db의 id/pwd와 일치하는지 확인하는 함수 호출


def join_member():  # 회원가입하는 함수
    global cust_info
    check = 0

    print(f"[ 회원가입하기 ]")

    while check != 1:

        conn = pymysql.connect(  # DB 연결
            host='127.0.0.1', user='root', password='123456',
            db='book_management', charset='utf8')
        cursor = conn.cursor()

        print(f"ID를 입력하세요 : ")
        cust_id = input()

        sql = '''
        SELECT cust_id FROM member_info
        '''
        cursor.execute(sql)  # SQL문 실행
        result = cursor.fetchall()  # 쿼리문의 출력결과 전부 가져오기

        for i in range(len(result)):  # 이미 DB에 있는 아이디일 경우
            if result[i][0] == cust_id:
                print("이미 가입된 ID입니다.")
                check = 1  # while문 빠져나오기

        if check == 0:  # DB에 없는 아이디일 경우
            cust_info.append(cust_id)  # cust_info 리스트에 요소들을 임시 저장
            print(f"PW를 입력하세요 : ")
            cust_pw = input()
            # print(cust_pw)
            cust_info.append(cust_pw)
            print(f"핸드폰 번호를 입력하세요(숫자만 입력) : ")
            cust_phone = input()
            # print(cust_phone)
            cust_info.append(cust_phone)

            sql = '''
                INSERT INTO member_info (cust_id, cust_pw, phone_number)
                VALUES (%s, %s, %s)
                '''
            cursor.execute(sql, (cust_info[0], cust_info[1], cust_info[2]))
            conn.commit()
            cursor.close()
            conn.close()
            cust_info = []  # cust_info 초기화
            break


while num != 3:

    try:
        print(promt)
        num = int(input())
        if num == 1:
            join_member()
        elif num == 2:
            account_login()
        else:
            print("잘못된 입력입니다. 1~3의 숫자를 입력해주세요.")

    except (ValueError, TypeError) as error:
        print('올바르지 않은 입력입니다. 다시 입력해 주세요.')
        continue

    else:
        if num == 3:
            print("프로그램을 종료합니다.")
            break