---
title: Innertube API 사용시 주의점
date: 2022-01-12 22:28:00 +0900
tags: [프로그래밍, 파이썬, 분석, 팁, API]
---

## 개요

Innertube API가 뭔지는 아래 링크를 참조하자.

[Pytube를 분석하며 Inntertube 알아보기 ](https://gabriel-dropout.github.io/posts/%EC%9C%A0%ED%8A%9C%EB%B8%8C-%EB%8F%99%EC%98%81%EC%83%81-%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C-%EB%AA%A8%EB%93%88-Pytube-%EB%B6%84%EC%84%9D%ED%95%98%EA%B8%B0)

이전에 유튜브 동영상 다운로드 속도 이슈를 해결하기 위해 청크 단위로 데이터를 쪼개 받는 스트림 기능을 직접 구현하였다.

그랬는데 이번에 또 속도 이슈가 터졌다. 다시 원인을 찾아 헤매기 시작했다.

---

## 원인은 API 요청에서

처음엔 역시 ___stream___ 구현 부분에서 뭔가 잘못된 거라고 생각했다. 근데 어제까지만 해도 잘 됐는데...?

그런데 아무리 봐도 이상한 부분이 없었다. ~~(Pytube랑 똑같이 만들었는데...?)~~

아무튼 내 잘못된 판단으로 수 시간 동안 삽질했는데, 원인은 허무할 정도로 별거 아닌 곳에 있었다.

```python
def get_info(self, video_id, client='android'): # 이 값이 web으로 되어 있었다
    headers = {'Content-Type': 'application/json', "User-Agent": "Mozilla/5.0", "accept-language": "ko_KR,en-US;q=0.8,en;q=0.6"}
    data = {
            'android':{'context': {'client': {'clientName': 'ANDROID', 'clientVersion': '16.20'}}},
            'android_embed':{'context': {'client': {'clientName': 'ANDROID', 'clientVersion': '16.20','clientScreen': 'EMBED'}}},
            'web':{'context': {'client': {'clientName': 'WEB','clientVersion': '2.20200720.00.02'}}},
            'web_embed':{'context': {'client': {'clientName': 'WEB','clientVersion': '2.20200720.00.02','clientScreen': 'EMBED'}}}
        }
```

줄바꿈 때문에 뭔가 보기 어려워진 것 같지만 아무튼...

`Innertube API`를 사용할 때 클라이언트 정보를 함께 보내는데, 어제 무의식 중에(?) 저 값을 __web__ 으로 바꿔 놓은 것이 문제였다. 똑같은 형식의 json 데이터를 반환하니 아무 의심을 하지 못했다.

그러나 __web 으로 요청해서 돌아온 응답의 url은 겉보기엔 멀쩡하지만, 다운로드 속도가 처참하다.__ __android__ 로 요청한 경우에 비해 속도가 100분의 1정도밖에 되지 않는 것 같다.

이유는 구글신만이 알고 있지 않을까...

---

## 여담

혹시 다른 클라이언트로 요청하면 다운로드 속도가 높아지지 않을까? 관련 자료를 조사해 봐야겠다.

저거 하나 때문에 몇 시간을 쓴 게 믿기지 않는다. 그래도 결국 해냈다 8^8
