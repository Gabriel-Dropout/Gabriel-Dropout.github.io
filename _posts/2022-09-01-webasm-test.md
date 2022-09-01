---
title: webasm test (feat.verlet)
date: 2022-09-01 20:17:00 +0900
tags: [test, raylib]

---

## 개요

이 포스트는 웹어셈블리 애플리케이션의 실행 여부를 확인하기 위해 작성되었습니다.

The purpose of this post is to see if the WebAssembly application can be run in Jekyll.

---

## 웹어셈블리 앱 예시

Verlet integration을 이용하면 입자의 위치 제약을 매우 쉽게 구현할 수 있다.

위치 제약은 시뮬레이션을 멋져 보이게 만드는 매우 강력한 도구이므로, 프로그래밍을 잘 모르는 사람에게 생색내기에 안성맞춤이다.

코드를 대충 휘갈겨도 아래 예시처럼 뭔가 있어 보이게 되는 것.

{::nomarkdown}
<canvas class=emscripten id=canvas oncontextmenu=event.preventDefault()></canvas>
<script src=/webasm/chain.js async></script>
{:/nomarkdown}

물리 환경을 구현하는 핵심 로직이 수십 줄에 불과하다는 점을 감안하면 매우 고무적인 결과가 아닐 수 없다.

---

## 여담

이 글을 쓰는 시점에서는 정상적으로 작동되는지 모르는 상태입니다.

잘 실행되는지 어떤지, 여러분은 알고 있겠네요. 제발 성공했으면...