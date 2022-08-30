---
title: wargame opa 풀이
date: 2022-08-28 20:04:00 +0900
tags: [웹해킹, 삽질]

---

## 개요

이 문제를 푸는 데만 이틀이 걸렸다.

전혀 어려운 문제가 아닌데도 말이다.

오라클 패딩 어택 문제인 것도 알고 있었고, 해당 공격 과정에 대해서도 확실히 알고 있었으나, 요청이 무슨 인코딩 방식을 사용했는지를 몰라서 한참 헤맨 것.

바보같은 삽질 과정은 걷어내고 핵심적인 사고 과정만 살펴보자. 전부 담기엔 여백이 부족하다. 부족하고말고.

---

## 문제 상황

http://ubuntu32.goatskin.kr/crypto/opa

어느 서버로 보내진 요청 로그가 주어진다. 아무튼 플래그를 얻자.

```http
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /8LU7LaBB_KSe8LmDkGCzRaIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 200
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67QKIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67QaIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67QqIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67Q6IeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67RKIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67RaIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz67R6IeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 403
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz4ARKIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
1.2.3.4 - [Sat Mar  5 01:37:37 2011] "GET /bgY_9ZIe9pz8P-r9kz4BRKIeorRgX4RBdRsmYdZzjx0 HTTP/1.0" 500
...
```

---

## 이론

__오라클 패딩 어택__ 이 사용된다. 사전 지식으로 __대칭키 암호화, CBC 블록 체인 모드__ 에 대한 지식도 필요하다.

[opa란?] (https://bperhaps.tistory.com/entry/%EC%98%A4%EB%9D%BC%ED%81%B4-%ED%8C%A8%EB%94%A9-%EA%B3%B5%EA%B2%A9-%EA%B8%B0%EC%B4%88-%EC%84%A4%EB%AA%85-Oracle-Padding-Attack)

---

## 관찰

`GET` 요청이다. 요청 URI와 `status_code`가 눈에 띈다.

URI는 암호문으로 보이고, 해당 암호문을 복호화했을 때 특정 데이터가 나오면 __200__ 을, 다른 평문이 나오면 __403__ 을, 해석 불가능한 경우 __500__ 을 반환하는 것으로 추측된다.

원래의 평문이 바로 구하고자 하는 FLAG라고 보는 게 합리적이다.

---

## 추측

opa 문제이므로 CBC 블록 암호화 방식이라고 가정하자.

요청URI들을 위에서부터 읽으면 문자열이 중간쯤부터 바뀌기 시작하므로 앞쪽이 __iv__ , 뒤쪽이 __cipher__ 라고 볼 수 있겠다.

```
original: bgY_9ZIe9pz8P-r9kz67QaIeorRgX4RBdRsmYdZzjx0
iv:       bgY_9ZIe9pz8P-r9kz67Qa
cipher:   IeorRgX4RBdRsmYdZzjx0
...라고 굳게 믿었다...
```

URI 경로에 해당하는 문자열은 어떤 바이트열의 문자열 인코딩 상태일 것이다. _base64_ 라고 생각하기에는 `-`와 `_`가 보인다. 따라서 _utf-8_ 인코딩으로 해석했다.

__이 가정 때문에 이틀 내내 이 문제만 붙잡고 있게 되리라고는, 당시에는 미처 생각하지 못했다.__

---

## 불규칙적인 패턴

일반적인 opa에서는 패딩 매칭을 시도하는 바이트 부분의 값을 1씩 증가시켜 가며 브루트 포스를 진행할 것이다. 꼭 그러라는 법은 없지만 도대체 누가 다른 방법을 시도한단 말인가. 그러나 로그에 이상한 부분이 너무 많았다.

```
 ('bgY_9ZIe9pz8P-r9kz67QqIeorRgX4RBdRsmYdZzjx0', '500')
 ('bgY_9ZIe9pz8P-r9kz67Q6IeorRgX4RBdRsmYdZzjx0', '500')
                        ^ watch this
```

특히 위처럼 `q`가 `6`으로 바뀌는 부분도 존재하는데, `utf-8` 인코딩에서는 q의 아스키 코드가 `0x71`, 6의 아스키 코드가 `0x36`이므로 줄어드는 것은 부자연스럽다. 항상 이런 것도 아니고, 또 절반 이상은 제대로 1씩 증가한다.

이를 비롯해 몇 가지 눈에 띄는 불규칙적인 패턴 때문에 결국 해석을 포기했었다.

---

## Base64 Url Safe

다음 날, 로그 텍스트를 뚫어져라 쳐다보다가 뭔가 떠올라 base64 인코딩 표를 찾아봤다.

q는 42, 0은 58... 정확히 16만큼 차이난다.

이때 base64가 정답이었음을 확신했다.

그러나 여전히 문제가 남아있었는데, 맨 처음 말했듯 base64 인코딩표에는 하이픈과 언더바가 존재하지 않는다. 그러던 중...

___Base64 Url Safe___

라는 걸 발견하고 말았다.

아니 그니까 웹으로 전송할 때는 `+`랑 `/`가 안 되니까 `-`랑 `_`로 대체한다는 뭐 그런...

이 사실을 몰랐으니 정말 어처구니가 없었다. 그렇게 전부 치환한 뒤에, 패딩 문자 `=`를 임의로 추가하고 디코딩을 해 보니

```
6e 06 3f f5 92 1e f6 9c fc 3f ea fd 93 3e bb 40 a2 1e a2 b4 60 5f 84 41 75 1b 26 61 d6 73 8f 1d 
6e 06 3f f5 92 1e f6 9c fc 3f ea fd 93 3e bb 41 a2 1e a2 b4 60 5f 84 41 75 1b 26 61 d6 73 8f 1d 
6e 06 3f f5 92 1e f6 9c fc 3f ea fd 93 3e bb 42 a2 1e a2 b4 60 5f 84 41 75 1b 26 61 d6 73 8f 1d 
6e 06 3f f5 92 1e f6 9c fc 3f ea fd 93 3e bb 43 a2 1e a2 b4 60 5f 84 41 75 1b 26 61 d6 73 8f 1d 
                                              ^ watch this
```

정확히 32바이트이고, 뒤에서 16번째 바이트의 값이 1씩 증가하는 것을 볼 수 있다.

즉 16바이트씩 나눴을 때 more significant한 무문이 iv, 나머지 부분이 cipher인 셈이다.

한술 더 떠서 403에러를 띄운 16개 리퀘스트의 iv부분에 차례로 0x01, 0x02 ... 0x16를 xor하여 결과를 보니

```
6f 07 3e f4 93 1f f7 9d fd 3e eb fc 92 3f ba 46 
6c 04 3d f7 90 1c f4 9e fe 3d e8 ff 91 3c b0 46 
6d 05 3c f6 91 1d f5 9f ff 3c e9 fe 90 63 b0 46 
6a 02 3b f1 96 1a f2 98 f8 3b ee f9 f5 63 b0 46 
6b 03 3a f0 97 1b f3 99 f9 3a ef e6 f5 63 b0 46 
68 00 39 f3 94 18 f0 9a fa 39 d0 e6 f5 63 b0 46 
69 01 38 f2 95 19 f1 9b fb 9b d0 e6 f5 63 b0 46 
66 0e 37 fd 9a 16 fe 94 ae 9b d0 e6 f5 63 b0 46 
67 0f 36 fc 9b 17 ff 94 ae 9b d0 e6 f5 63 b0 46 
64 0c 35 ff 98 14 cc 94 ae 9b d0 e6 f5 63 b0 46 
65 0d 34 fe 99 02 cc 94 ae 9b d0 e6 f5 63 b0 46 
62 0a 33 f9 f9 02 cc 94 ae 9b d0 e6 f5 63 b0 46 
63 0b 32 60 f9 02 cc 94 ae 9b d0 e6 f5 63 b0 46 
60 08 4f 60 f9 02 cc 94 ae 9b d0 e6 f5 63 b0 46 
61 d4 4f 60 f9 02 cc 94 ae 9b d0 e6 f5 63 b0 46 
b5 d4 4f 60 f9 02 cc 94 ae 9b d0 e6 f5 63 b0 46
```

오른쪽부터 하나씩 맞춰지는, 매우 교과서적인 오라클 패딩 어택의 과정을 볼 수 있었다.

이때 마지막 바이트열이 바로 __IV ^ 평문__ 이 된다.

맨 처음 요청의 status code가 200이므로, 여기서 정상 iv를 추출하고 위의 결과와 xor한 후 얻어진 바이트열을 utf-8 인코딩해 보니 플래그가 나왔다.

---

## 여담

웹용 base64 인코딩이 있다는 사실을 알았다면 30분도 채 걸리지 않았을텐데 참...

기초가 중요함을 다시 한 번 깨닫게 된다.

아까운 시간을 낭비했으니 당분간은 열심히 살아야겠다. 아이 아까워.