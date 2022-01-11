---
title: Youtube DASH 동영상 다운로드 속도 이슈(해결)
date: 2022-01-11 21:38:00 +0900
tags: [프로그래밍, 분석, 팁]
---

## 개요

저번 Pytube를 분석글에서 새로운 API를 발견하는 부분까지 다뤘었다.

[Pytube_분석하기](https://gabriel-dropout.github.io/posts/%EC%9C%A0%ED%8A%9C%EB%B8%8C-%EB%8F%99%EC%98%81%EC%83%81-%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C-%EB%AA%A8%EB%93%88-Pytube-%EB%B6%84%EC%84%9D%ED%95%98%EA%B8%B0)

이번에는 그 이후 이야기다. 동영상 소스 링크를 얻었으므로 `requests.get()`로 바이너리 데이터를 받아오는 게 일반적으로 그 다음에 할 일이라고 할 수 있다.

그러나 대용량 데이터라면? 전체 파일 다운로드가 완료될 때까지 프로그램이 멈춰 있을 것이다. Thread를 분리해도 되겠지만 메모리 문제 등 여러 가지를 고려했을 때 근본적인 해결책으로는 역시 Stream을 이용하는 것이 맞다.

즉 데이터를 작은 청크로 쪼개 받는 것이다. 파이썬의 `requests` 모듈은 이를 지원한다.

``` python
headers = {} #헤더는 알아서 설정
file = requests.get(url, stream = True, headers=headers)
#length = int(file.headers['Content-Length'])
with open('filename.mp4',"wb") as f:
    for chunk in file.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
```

`stream = True` 인자를 추가하면 이렇게 콘텐츠를 나누어 받을 수 있다. 문법이 좀 특이한데, 아무래도 제너레이터를 반환하는 모양이다.

---

## 이대로 끝날 리가 없지;

### 속도 문제

잘 되는 것처럼 보였으나 곧바로 이슈가 발생했다.

__Progressive__ 방식의 비디오는 빠르게 받아지는 반면 __Adaptive__ 방식의 비디오는 다운로드 속도가 매우 느려졌다.

관련 자료를 검색해 봤지만 특별히 도움 되는 이야기는 없었다. 유튜브 측에서 다운로드 못 받게 해 놓은 건가..?

---

### 크롬에서는 빠르게 작동한다

정작 링크를 타고 들어가서 직접 '다운로드' 버튼을 클릭하면 매우 빠른 속도로 다운로드가 된다. 무슨 차이일까. 요청 헤더를 죄다 복사해서 넣어 봤는데 마찬가지. 일단 기각.

---

### Pytube도 빠르게 작동한다

생각도 못했는데, Pytube를 이용해 같은 동영상을 다운로드해 보니 생각보다 빠르게 다운로드 되는 것을 확인했다. 무슨 차이일까. 코드를 보자.

`Stream` 클래스의 `download()` 함수 중 일부이다.

```python
for chunk in request.stream(
    self.url,
    timeout=timeout,
    max_retries=max_retries
):
    # reduce the (bytes) remainder by the length of the chunk.
    bytes_remaining -= len(chunk)
    # send to the on_progress callback.
    self.on_progress(chunk, fh, bytes_remaining)
```

`self.on_progress()`에는 데이터를 작성하는 코드가 있다. 즉 `request.stream()` 부분이 핵심인 것 같은데, 핵심은 바로

`range_header = f"bytes={downloaded}-{stop_pos}"`

즉 데이터 범위를 지정하는 헤더. 이를 이용해 직접 청크를 구현해 놓았던 것이다! 이를 깨닫고 부랴부랴 따라 구현해 봤다. get 요청만 있으면 되니 __requests__ 모듈도 필요 없다. 파이썬 기본 모듈인 __urllib.request__ 를 사용하면서 외부 종속성을 없앴다.

```python
def stream(url, chunk_size = 9437184):
    file_size = chunk_size  # fake filesize to start
    downloaded = 0
    while downloaded < file_size:
        stop_pos = min(downloaded + chunk_size, file_size) - 1
        range_header = f"bytes={downloaded}-{stop_pos}"

        headers.update({"Range": range_header})
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)

        if file_size == chunk_size: # get real filesize
            content_range = response.info()["Content-Range"]
            file_size = int(content_range.split("/")[1])
            print(file_size/1024/1024,'MB')
        
        chunk = response.read()
        downloaded += len(chunk)
        yield chunk
    return

with open('filename.mp4', "wb") as f:
    for chunk in stream(url):
        f.write(chunk)
```

`yield`를 이용해 `lazy evaluation`를 멋지게 구현한 점이 인상적이다.

한편 다운로드할 파일 크기를 알아내기 위해 따로 요청하지 않고, 가짜 데이터로 뒀다가 나중에 바꾸는 부분도 눈여겨볼 만하다. 트릭이라면 트릭이지만...

청크 사이즈는 Pytube에서 9MB로 뒀길래 나도 그렇게 했는데, 이유는 모르겠다. 단지 __15MB 이상으로 잡으면 `response.read()` 부분에서 멈추는 현상__ 이 생기길래 일단 그대로 냅뒀다.

아무튼 이렇게 하니 해결됐다. Chrome에서 다운로드하는 것보다 살짝 느린 감이 있지만 수용 범위라고 생각한다.

---

## 여담

해결하는데 상당히 오래 걸렸다. 매번 그렇지 뭐. 아무튼 다행이다.

근본 원인은 아직도 모르겠다. 역시 구글이 의도한 걸까?
