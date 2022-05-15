---
title: Wargame 풀이 - Easy_mathematics
date: 2022-05-16 02:28:00 +0900
tags: [해킹, pwntool]
---

## 개요

복습 겸, 블로그 글도 채울 겸 이전에 풀었던 해킹 문제들의 풀이를 작성해 보려고 한다.

몹시 귀찮지만 뭐라도 적어놓지 않으면 까먹고 말겠지.

---

## 문제 상황

```bash
nc remote goatskin.kr 10474
```

를 입력해 문제를 열어 보자.

```bash
nc remote.goatskin.kr 10474
--------------------------------
Welcome to easy mathematics class:D
If you find correct x in 20 questions, I will give you the flag!
597521 + x = 693337 (mod 1217207)
x =
```

20개의 수학 문제를 풀면 플래그를 준다고 친절히 설명되어 있다.

우선 첫 번째 문제를 풀어 보자. 간단한 합동식이다.

x = 693337- 597521+ 1217207=  __1313023__

```bash
1313023
--------------------------------
Correct!
555905243 + x = 591516923 (mod 1246223113)
```

일일이 다 풀 수는 없을 듯하다.

---

## pwntool을 이용한 자동화

파이썬 라이브러리를 이용해 문제를 자동으로 풀어 보자. 다음과 같은 파이썬 코드를 실행한다.

```python
import pwn

pwn.context.log_level = "debug"
p = pwn.remote("remote.goatskin.kr", 10474)

p.recvuntil("I will give you the flag!\n")
while True:
    a = int(p.recvuntil(" ").strip())
    p.recvuntil("+ x = ")
    b = int(p.recvuntil(" ").strip())
    p.recvuntil("(mod ")
    N = int(p.recvuntil(")").strip(b")"))
    
    p.sendline(str(b-a+N))
    p.recvuntil("Correct!\n")

p.interactive()
```

`pwn.context.log_level = "debug"`를 사용해야 송/수신 데이터를 전부 볼 수 있다.

`remote`함수로 서버에 접속하고,

`recvuntil`함수로 값을 수신하고,

`sendline`함수로 값을 송신한다.

마지막으로 `interactive`함수는 쉘을 통해 입력을 받게 한다. `nc`를 사용했을 때와 같은 상태가 된다.

실행 결과를 보자.

```bash
...
[DEBUG] Received 0x53 bytes:
    '759545235596293660373 - x = 596007530665219840709 (mod 1515652371985089270869)\n'
    'x = '
```

연산자가 빼기로 바뀌면서 더이상 문제를 풀지 못하게 됐다. 까다로운 녀석.

연산자를 파싱해서 계산을 다르게 해 보자.

```python
import pwn

pwn.context.log_level = "debug"
p = pwn.remote("remote.goatskin.kr", 10474)

p.recvuntil("I will give you the flag!\n")
while True:
    a = int(p.recvuntil(" ").strip())
    oper = str(p.recvuntil(" ").strip())
    p.recvuntil("x = ")
    b = int(p.recvuntil(" ").strip())
    p.recvuntil("(mod ")
    N = int(p.recvuntil(")").strip(b")"))

    if oper=='+':
        p.sendline(str(b-a+N))
    elif oper=='-':
        p.sendline(str(a-b+N))

    p.recvuntil("Correct!\n")

p.interactive()
```

실행 결과를 보자.

```bash
[DEBUG] Received 0x82 bytes:
    '1116226993351842646871993494858035457 * x = 1145386473892459772998729269526538141 (mod 1757595265093982918604179042983262779)\n'
    'x = '
```

이번엔 곱셈이다. 모듈러 곱셈 역원을 구하는 문제이므로 확장 유클리드 호제법을 이용해 보자.

코드를 다음과 같이 수정한다.
```python
import pwn

def euclid(a, b):
    n1 = [1,0,a]
    n2 = [0,1,b]
    tmp = [0,0,0]
    while n2[2]>1:
        tmp = list(n2)
        p = n1[2]//n2[2]
        n2 = [n1[0]-n2[0]*p, n1[1]-n2[1]*p, n1[2]-n2[2]*p]
        n1 = tmp
    return n2[0]

pwn.context.log_level = "debug"
p = pwn.remote("remote.goatskin.kr", 10474)

p.recvuntil("I will give you the flag!\n")
while True:
    a = int(p.recvuntil(" ").strip())
    oper = str(p.recvuntil(" ").strip())
    p.recvuntil("x = ")
    b = int(p.recvuntil(" ").strip())
    p.recvuntil("(mod ")
    N = int(p.recvuntil(")").strip(b")"))

    if oper=='+':
        p.sendline(str(b-a+N))
    elif oper=='-':
        p.sendline(str(a-b+N))
    elif oper=='*':
        p.sendline(str((euclid(a,N)+a*N)*b))

    p.recvuntil("Correct!\n")

p.interactive()
```

음수를 전달하면 안 되기 때문에 `euclid(a,N)`대신 `euclid(a,N)+a*N`를 넣은 부분에 주목하자.

실행 결과는

```bash
[DEBUG] Received 0x36 bytes:
    'Good! Here is the flag : ******_**********_**********\n'
```

플래그를 얻었다.

---

## 여담

밀린 과제 하기 싫어서 포스팅이나 하는 중... 내일의 나야 미안해!