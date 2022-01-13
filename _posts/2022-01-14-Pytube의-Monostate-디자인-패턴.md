---
title: Pytube의 Monostate 디자인 패턴
date: 2022-01-14 00:18:00 +0900
tags: [프로그래밍, 파이썬, 팁, 분석]
---

## 개요

__youpi__ 모듈을 만들면서 한 가지 문제 상황에 부딪혔다. 정리하면 다음과 같다.

1. `YouTube` 객체는 한 개의 `StreamList` 객체 주소, 동영상 제목 `self.title`을 가진다.
2. `StreamList` 객체는 여러 개의 `Stream` 객체 주소를 가진다.
3. `Stream` 객체는 `download()` 함수를 제공한다.
4. `download()`는 `title` 인자가 없으면 동영상 제목을 파일 제목으로 자동 지정한다.

![그림으로 보자](https://user-images.githubusercontent.com/88845385/149362685-86d170aa-4c35-4b0c-8c9a-d920b0925407.png)

바로 참조관계가 순환하는 문제다. 떠오른 해결 방법은

- 각 `Stream`객체를 생성할 때마다 제목을 인자로 넘겨주어 __instance variable__ 로 저장한다.
- 어차피 주소만 저장하므로 `YouTube` 객체를 인자로 넘긴다.

첫 번째는 같은 데이터가 중복된다는 단점이 있고, 두 번째는 상당히 문제가 많은 구조이다.

고민할 시간에 PyTube의 코드를 훔쳐 보자(?)

---

## 자칭 Monostate... 아님 Borg

1. 이런  친구를 정의한다.

   ```python
   class Monostate:
       def __init__(
           self,
           on_progress: Optional[Callable[[Any, bytes, int], None]],
           on_complete: Optional[Callable[[Any, Optional[str]], None]],
           title: Optional[str] = None,
           duration: Optional[int] = None,
       ):
           self.on_progress = on_progress
           self.on_complete = on_complete
           self.title = title
           self.duration = duration
   ```

2. `YouTube` 클래스의 `__init__()`에서

   ```python
   self.stream_monostate = Monostate(
       on_progress=on_progress_callback, on_complete=on_complete_callback
   )
   ```
   
3. 스트림을 생성할 때

   ```python
   video = Stream(
       stream=stream,
       monostate=self.stream_monostate,
   )
   ```

상당히 멋진 아이디어다. 그런데 Monostate(파이썬에선 Borg라고 하는 것 같다) 패턴은 아무리 봐도 아니다.

애초에 객체가 하나다. 생성자를 private으로 강제하는 건 아니지만 __일단 한 번만 생성하고, 그 주소를 모든 `Stream`이 공유하고 있다.__ ___싱글톤이다.___

뭐 아무튼... 디자인 패턴을 잘 활용했다.

---

## 결론

모순이 발생하진 않지만 뭔가 구조가 복잡해지는 느낌이랄까.

다른 방법이 없는지 좀 더 고민해 봐야겠다.

결국 저 방법을 따라갈 것 같기는 하다.

