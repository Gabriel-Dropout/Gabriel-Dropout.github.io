---
title: 뭔가 이상한 ebook viewer 만들기(1)
date: 2022-01-21 20:17:00 +0900
tags: [프로그래밍, JS, HTML, 개발, 삽질]
---

## 개요

<span style="color: red;">*두서 없는 장황한 글이므로 그 누구도 읽지 않을 것을 권장합니다.</span>

### 사건의 발단

이 프로젝트는, 사실 늘 그렇듯, 꼬리에 꼬리를 무는 상상의 저편에서 나타나는 _'개쩌는 아이디어 한 조각'_ 에서 비롯되었다.

무슨 일인고 하니, 문득 영어 공부를 시작해야겠다는 생각이 들었던 것이다.

영어로 된 글을 읽으며 독해 연습을 하는 게 좋겠다 싶었다.

이왕 읽는 거 재미있는 책을 읽으면서 재미있게 하고 싶었다.

영어로 된 라이트노벨을 검색해 봤다.

구매를 하려고 했는데 온라인 서점은 보이지 않고 대신

https://archive.org

에서 PDF파일을 제공하고 있었다. 비영리 단체라고 하는데, 저작권 문제에 대한 명확한 사실은 파악하기 어려웠다. 이는 추후 이야기하도록 하고, 아무튼 이 파일을 실행해 봤다.

온통 영어다. 모르는 문장을 드래그해서 자동 번역할 수 있으면 좋을 것 같다.

### 파파고 번역 (크롬 확장 프로그램)

![파파고](https://user-images.githubusercontent.com/88845385/150519785-871385fa-1a2d-475e-b5a0-d5c4b5766c38.png)

있었다(!)

그러나 PDF 뷰어로 열린 문서의 Text는 확장 프로그램에서 감지하지 못했다.

HTML 본문 내에 텍스트가 노출되어 있지 않기 때문인 듯했다.

PDF를 HTML로 바꿔 보자.

### PDF to HTML

https://www.sodapdf.com/ko/pdf-to-html/

여기서 바꿀 수 있다.

그런데 막상 열어 보니

![막상 열어 보니...](https://user-images.githubusercontent.com/88845385/150520409-e16ef54d-218d-4105-9e22-d32cd8a13248.png)

짱 구렸다.

### 그럼 어떡하지?

가볍게 영어 공부를 하려고 했는데 방해 요소가 너무 많다. 문제를 해결하기 위해 위의 html 구조를 파악해 보자.

메인 __html__ 파일 코드를 보면,

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
</head>
<frameset cols="150,*">
    <frame name="pageindex" src="OutDocument\pg_index.htm" />
    <frame name="contents" src="OutDocument\pg_0001.htm" />
</frameset>
<noframes>
    <body>
        <p>This page uses frames, but your browser doesn't support them.</p>
    </body>
</noframes>
</html>
```

잘 모르겠지만 `frame`은 다른 html 파일을 화면에 불러오는 요소로 추정된다.

`pageindex`는 문서 왼쪽의 인덱스, `contents`는 본문인 것 같다.

```bash
.
├─ OutDocument
│  │  ci_1.png
│  │  ci_2.png
│  │  pg_0001.htm
│  │  pg_0002.htm
│  │  pg_index.htm  # 목차
│  │  vi_1.png
│  └─ vi_2.png
└─ OutDocument.htm  # 메인
```

전체 폴더는 이런 구조다. static한 문서의 표준이라고 할 만큼 정석적인 구조다. 사실 내부 구조는 처음 보는데 왠지 그럴 것 같다.

## 아무튼 새로 개발하는 걸로!

상단의 파일 구조를 그대로 가져오면서, `OutDocument.htm`을 수정해서 멋진 뷰어를 만들어 보자.

자바스크립트와 html은 제대로 배우지 않았으므로 클론 코딩으로 해결하기로 했다.

다음 영상을 참고하자.

[Let's make a Flip Book using HTML CSS JavaScript](https://www.youtube.com/watch?v=0kD6ff2J3BQ)

## 로직 분석

튜토리얼이라 그런지 __plain한 javascript__ 인 점이 마음에 든다. 프레임워크를 쓰기 시작하면 이제... 강좌별로 사용하는 프레임워크가 제각각이라 그대로 쓰기도 뭐하고, 따로 구현하기도 매우 까다롭기 때문이다.

`index.html`, `main.js`, `style.css`로 이루어져 있다.

`index.html`의 헤더 부분이다.

```html
<head>
    <meta charset="UTF-8">
    <title>Book</title>
    <link rel="stylesheet" href="./style.css">
    <script src="./main.js" defer></script>
    <script src="https://kit.fontawesome.com/b0f29e9bfe.js" crossorigin='anonymous'>
    </script>  <!--여기-->
</head>
```

강조한 부분은 _fontawesome_ 이라는 웹사이트에서 제공하는 기능인 것 같은데, 버튼에 쓰일 아이콘을 불러오기 위해 적었다.

```html
<!-- Previous Button-->
<button id="prev-btn">
    <i class="fas fa-arrow-circle-left"></i>
</button>
```

이런 식으로 불러올 수 있다.

```html
<div id="book" class="book">
    <!-- Paper 1 -->
    <div id="p1" class="paper">
        <div class="front">
            <div id="f1" class="front-content">
                <h1>Front 1</h1>
            </div>
        </div>
        <div class="back">
            <div id="b1" class="back-content">
                <h1>Back 1</h1>
            </div>
        </div>
    </div>
    <!-- Paper 2 -->
    반복...
</div>
```

다소 충격적이지만, book 안에 페이지가 하드코딩되어 있다.

각 페이지에는 앞면과 뒷면이 차례로 정의되어 있다.

css를 올바르게 작성하는 게 중요해 보인다.

__다음은 `style.css`중 일부인데,__

```css
body {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;

    font-family: sans-serif;
    background-color: powderblue;
}
```

`100vh`는 뷰포트 높이의 100%를 의미한다.

`display: flex`는 컨테이너 레이아웃 설정인데, 기본적으로 가로 방향으로 엘리먼트를 정렬한다.

`justify-content: center;`는 주축(가로축)을 중앙 정렬,

`align-items`는 수직축을 중앙 정렬한다.

```css
.front {
    z-index: 1;
    backface-visibility: hidden;
    border-left: 3px solid powderblue;
}

.back {
    z-index: 0;
}
```

`z-index`는 요소의 깊이로, 높을수록 앞에 위치한다.

`backface-visibility`는 입체 회전 등에 의해 요소가 뒤집어질 경우 화면에 표시할 형태를 지정한다.

```css
.flipped .front,
.flipped .back {
    transform: rotateY(-180deg);
}
```

페이지에 `flipped` 클래스가 붙으면 그 하위의 앞면, 뒷면이 회전하며 책장이 넘어가는 애니메이션을 연출한다. 그냥 page에 rotateY()를 걸어도 될 것 같은데 모지...?

다음으로 `main.js`를 보자.

```javascript
prevBtn.addEventListener("click", goPrevPage);
nextBtn.addEventListener("click", goNextPage);
```

HTML 상에서 버튼 엘리먼트에 함수를 언급하는 대신 이벤트 리스너를 달았다.

```javascript
function goNextPage() {
    if(currentLocation < maxLocation) {
        switch(currentLocation) {
            case 1:
                openBook();
                paper1.classList.add("flipped");
                paper1.style.zIndex = 1;
                break;
            case 2:
                paper2.classList.add("flipped");
                paper2.style.zIndex = 2;
                break;
            case 3:
                closeBooktoEnd();
                paper3.classList.add("flipped");
                paper3.style.zIndex = 3;
                break;
            default:
                throw new Error("unknown state");
        }
        currentLocation++;
    }
}
```

......설명은 생략.

```javascript
function openBook() {
    book.style.transform = "translateX(50%)";
    prevBtn.style.transform = "translateX(-180px)";
    nextBtn.style.transform = "translateX(180px)";
}
function closeBooktoBegin() {
    book.style.transform = "translateX(0%)";
    prevBtn.style.transform = "translateX(0px)";
    nextBtn.style.transform = "translateX(0px)";
}
function closeBooktoEnd() {
    book.style.transform = "translateX(100%)";
    prevBtn.style.transform = "translateX(0px)";
    nextBtn.style.transform = "translateX(0px)";
}
```

`translateX`는 기준점에 대한 엘리먼트의 x좌표라고 생각하면 될 것 같다. 책을 열고 닫을 때 재생되는 애니메이션을 연출한다.

## 결과

![book_gif](https://user-images.githubusercontent.com/88845385/150551573-fd6b6f60-3dbb-4ccb-87d0-f6bf3eb3dc99.gif)

## 다음화 예고

너무 길어서 나머지는 다음 포스트에서 다루는 게 좋을 듯하다. 라이트노벨을 읽기 위한 여정은 멀고도 험난하다. 아래에 업데이트 목록을 작성해 뒀다.

## 추가할 기능

- [ ] 하드코딩된 부분을 좀 손보고, frame을 이용해 페이지 내용에 html 문서를 넣어 보자.
- [ ] 비효율적인 코드가 보인다. 최적화하자.
- [ ] 배경색을 선택할 수 있게 만들자.
- [ ] 그냥 테마 프리셋을 선택하게 하자.
- [ ] 책을 확대할 수 있게 만들자.
- [ ] 확장 프로그램 없이 Papago API를 이용해 네이티브로 번역 기능을 넣어최적화된 인터페이스 및 사용자 환경을 조성하자.
- [ ] 임의의 pdf파일을 불러와 형식에 맞는 html 문서로 변환, 책으로 보여주는 기능을 추가하자.
- [ ] 웹서버에 올리자.
- [ ] 도메인을 설정하자.
- [ ] 쿠키 등의 기능을 이용해 사용자별 책장(도서 목록)을 제공하자.
- [ ] 너무 스케일이 커져 버렸다.

3일 내에 완성하지 않으면 흥미가 떨어질 것이므로 최대한 빠르게 구현해 보자.
