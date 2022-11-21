---
title: Google Drive Image Uploader 완성
date: 2022-11-19 16:59:00 +0900
tags: [C#, gui]
---

## 개요

파이썬으로 제작했던 이미지 업로더 프로토타입을 제대로 완성해보기로 했다.

gui 개발에 사용될 라이브러리를 선택해야 하는데, 그대로 파이썬으로 개발할 생각이라면 사실상 `PyQT`정도가 있겠다. 그러나 저 프레임워크에 그다지 좋은 기억은 없어서, 아예 다른 언어를 사용해보기로 했다.

고민하던 차 역시 윈도우 네이티브 앱 개발엔 C#이 낫겠다는 생각이 들었다. 자바를 싫어하고 C#을 한 번도 사용해본 적이 없었기에 고민이 되었지만 그런 사소한 문제가 나의 앞길을 막을 수는 없으리라.

> 아래에 서술된 모든 내용에는 심각한 개념 오류가 있을 수 있습니다.

---

## 1일 차

예전에 **Humble Bundle**에서 구매 후 방치해 뒀던 케케묵은 책 **C# in a Nutshell**을 꺼내보았다. 이렇게 말하지만 사실 E북이다.

<img src="https://drive.google.com/uc?id=1Ek_z-2lYy_EG3d0g-stmYyYj5RuU2mUO" alt="C# in a Nutshell" style="zoom:67%;" />

한국어로 번역하면 **간단히 정리한 C#**정도가 되려나. 언어 레퍼런스 같은 느낌으로 쓰여 있어서 처음 보기엔 적합하지 않지만 가진 책이 이것밖에 없어서(...) 울며 겨자 먹기로 정독했다.

첫인상은 생각보다 놀라웠다. 닷넷프레임워크의 존재는 가볍고 종속성 없는 소프트웨어를 지향하는 입장에서 다소 거북하게 느껴지지만, **윈도우 OS에 기본적으로 설치되어 있다는 사실**이 위안이 되었다. 오히려 신경써야 할 부분이 줄어든 느낌이랄까. 물론 요새 MS에서 밀고 있는 차세대 프레임워크인 .NET은 또 기본 탑재가 아니라 좀 의아하다. 멀티 플랫폼을 위해서겠지.

대규모 협업 프로젝트의 안정성을 보장하기 위해 **고도로 추상화되고 캡슐화된 언어 설계**는 감탄을 자아냈다. 언어 구조 설계 분야의 덕후가 만든 게 분명하다. 물론 JAVA도 비슷한 느낌이겠지만 나는 자바를 모르니까.

뭐 그건 그렇다 치고, 본인은 잘 사용하기만 하면 되는 입장이라 C++과의 차이점을 대충대충 훑어보고 첫째 날이 마무리되었다.

---

## 2일 차

GUI 개발이 필요하기 때문에 관련 정보를 찾아봤다. 크게 `Winform`과 `WPF`가 있는 것 같았다. 윈폼은 아주아주 옛날에 사용되던 방식이라나 뭐라나. 이왕이면 최신 트렌드를 따라야겠다 싶어 WPF로 선택했다.

WPF는 `MVVM` 디자인 패턴을 염두에 두고 설계되었다고 한다. 디자인 패턴일 뿐이니까 반드시 따를 필요는 없겠지만 그래도 시키는 대로 하는 착한 개발자가 되어야지.

**MVVM**이란 전체 로직을 **Model, View, Vi\ewModel**의 세 단위로 철저히 분리해서 개발하는 방식으로 보인다. 각각 데이터 구조, 유저 인터페이스, 뷰와 모델 간의 연결장치 정도로 보인다. 뷰모델에 실제로 핵심적인 로직이 들어가는 것 같다.

**MVVM**에서 특히 신경써야 하는 점은, **뷰모델은 실제로 UI가 어떻게 구성되는지 모른다**는 점이다. 그러니까 UI단에서 필요할 법한 함수(로그인 요청, 파일 업로드 등등)를 구현하지만, 이것을 버튼과 연결하는 작업은 **View**에서 이루어지는 듯하다. 만들어 보면 알겠지 뭐.

---

## 3일 차

유튜브 영상을 보면서 클론 코딩을 두세 번 해 봤다. 뷰 레이아웃을 구성할 때는 `XAML`이라는, HTML 비슷한 무언가로 작업하는데 다른 것보다 애니메이션 작업이 좀 골때린다. MVVM 때문에 로직에서 직접 애니메이션을 구성할 수 없는데, 이걸 XAML로 처리하려니 또 잘 모르겠다. 흠.

---

## N일 차(?)

심각한 귀찮음으로 인해 한동안 미루고 또 미루다가 늦어지고 말았으나... 결국 하루 만에 완성했다. 진작 할 걸.

<img src="https://drive.google.com/uc?id=1UTHOCn9n1G5mXZzozg-h8wcPm0lj9vnF" alt="image uploader" style="zoom:50%;" />

짜잔.

기능은 다음과 같다.

- 맥OS를 사용하는 듯한 윈도우

  기존 윈도우 타이틀바를 없애고 커스텀으로 만들었다. 맥 UI를 적극 참고했다.

- 파일 탐색 및 D&D

  **파일 탐색기** 뿐 아니라 **드래그 앤 드롭**으로도 업로드 가능하다. 여러 개의 이미지 파일을 한 번에 올릴 수도 있지만 업로드 자체는 순차적으로 처리된다. 이미 비동기 방식이라 한 번에 처리할 수 있긴 하지만 굳이 그렇게 만들 필요는 없어 보인다.

- 업로드 리스트 확인 및 클립보드 복사

  오른쪽에 파일별 업로드 과정이 출력되며 기록을 삭제할 수 있다. 해당 아이템을 클릭하면 URL이 클립보드에 복사된다.

- 로그인 기능

  처음 업로드를 시도할 때 **웹브라우저를 통해 구글 로그인을 요구**한다. 30초 내에 완료해야 하는데 생각해 보니 좀 널널하게 할 걸 그랬다. 현재 권한을 부여받은 계정만 사용할 수 있다.

---

## 개발하면서 얻은 팁

쉽게 서술하긴 했지만 사실 여러 난관이 있었다.

### 프레임워크 없이 함수 바인딩하기

**MVVM** 패턴에서 함수를 바인딩할 때는 `ICommand` 인터페이스를 상속한 클래스를 참조하게 된다. 중요한 점은 컨트롤의 `command` 프로퍼티에 이 객체가 바인딩되는 방식이지만 **해당 프로퍼티를 가진 객체가 기본적으로 Button밖에 없다는 사실.**

"파일을 사각형 범위 안에 드랍했을 때 호출되는 함수"는 **Rectangle** 컨트롤의 **Drop** 프로퍼티에 담기는데, 이것은 **ICommand** 객체를 못 받고 함수 자체만 받는다. **그리고 이 함수는 반드시 해당 뷰의 코드비하인드에서 생성해야 한다.**

다양한 MVVM 프레임워크를 사용하면 된다는 것 같지만 그러고 싶지는 않다. 간단한 해결법은 코드비하인드에서 다음과 같은 함수를 정의하는 것.

```c#
private void UploadWithDrop(object sender, DragEventArgs e)
{
    ((MainViewModel)DataContext).UploadWithDropExe(sender, e);
}
private void UploadWithBtn(object sender, System.EventArgs e)
{
    ((MainViewModel)DataContext).UploadWithBtnExe(sender, e);
}
private void CopyLink(object sender, System.EventArgs e)
{
    ((MainViewModel)DataContext).CopyLinkExe(sender, e);
}
private void RemoveItem(object sender, System.EventArgs e)
{
    ((MainViewModel)DataContext).RemoveItemExe(sender, e);
}
```

이런 식으로 뷰모델에서 선언한 함수를 코드비하인드에서 바인딩해주는 것이다. 편법에 가까운 방식이지만... 협업을 할 것도 아니고 규약만 잘 지키면 아무래도 상관없지 싶다.



### 애니메이션 스토리보드 제어

```XAML
<Path.Style>
    <Style TargetType="{x:Type Path}">
        <Setter Property="Data" Value="{StaticResource ProgressIcon}"/>
        <Setter Property="RenderTransform">
            <Setter.Value>
                <RotateTransform/>
            </Setter.Value>
        </Setter>

        <Style.Triggers>
            <DataTrigger Binding="{Binding Cancelled}" Value="true">
                <Setter Property="Data" Value="{StaticResource CancelIcon}"/>
                <DataTrigger.EnterActions>
                    <StopStoryboard BeginStoryboardName="sb"/>
                </DataTrigger.EnterActions>
            </DataTrigger>
            <DataTrigger Binding="{Binding Progress}" Value="100">
                <Setter Property="Data" Value="{StaticResource CompleteIcon}"/>
                <DataTrigger.EnterActions>
                    <StopStoryboard BeginStoryboardName="sb"/>
                </DataTrigger.EnterActions>
            </DataTrigger>

            <EventTrigger RoutedEvent="FrameworkElement.Loaded">
                <EventTrigger.Actions>
                    <BeginStoryboard Name="sb">
                        <Storyboard>
                            <DoubleAnimation
                                Storyboard.TargetProperty="(Path.RenderTransform).(RotateTransform.Angle)"
                                From="0.0" To="360" Duration="0:0:1" RepeatBehavior="Forever"/>
                        </Storyboard>
                    </BeginStoryboard>
                </EventTrigger.Actions>
            </EventTrigger>
        </Style.Triggers>
    </Style>
</Path.Style>
```

바인딩 되어있는 변수를 이용해 애니메이션을 제어하는 부분이 핵심이다. `StopStoryboard`로 재생중인 애니메이션 스토리보드를 멈출 수 있다.



### Datacontext의 값 변화를 감지

```c#
DataContextChanged += (e,v) => ((FileDetail)DataContext).PropertyChanged += TriggerAnimation;
```

이를테면 데이터컨텍스트의 값이 바뀔 때마다 progress bar의 애니메이션이 실행되게 구현하고 싶다고 하자.

데이터컨텍스트 객체가 `ObservableObject`를 상속받고 있다면, `PropertyChanged`  델리게이트 필드가 존재해야 한다. 따라서 여기에 원하는 함수를 바인딩할 수 있다. 단, 뷰는 모델을 알 수 없으므로 DataContext는 뷰모델에서 정의된 객체를 참조해야 할 것 같다.

`PropertyChanged`필드에 의존하지 않고 뷰모델에서 필요한 델리게이트를 직접 선언하고 관리하는 것도 방법이다.



### 코드비하인드에서 애니메이션 관리

뷰모델에서 컨트롤의 애니메이션을 조작하는 건 명백한 MVVM 패턴 위반이다. 그러나 코드비하인드는 View의 일부이므로 이를 조작할 수 있다. 물론 코드 가독성이 떨어지는 건 마찬가지겠지만.

```c#
public void TriggerAnimation(object sender, EventArgs e)
{
    var testanim = new DoubleAnimation
    {
        To = ((FileDetail)sender).Progress,
        Duration = TimeSpan.FromMilliseconds(2000)
    };
    testanim.EasingFunction = new CubicEase() { EasingMode = EasingMode.EaseInOut };
    Storyboard.SetTarget(testanim, pb);
    Storyboard.SetTargetProperty(testanim, new PropertyPath("Value"));

    var storyboard = new Storyboard();
    storyboard.Children.Add(testanim);
    storyboard.Begin();
}
```

---

## 여담

위의 팁 부분은 스택오버플로우를 무한 탐색하면서 터득한 개인적인 해결책에 불과하다. 공인된 방식이 아니므로 문제가 있을 수도 있다. 그러나 **겉보기에는 잘 작동하는 것처럼 보이며, 모두 이번 프로젝트에 사용되었다.**

이미지 업로더만 만들고 끝내기에는 C#을 배운 게 좀 아깝긴 한데... 더 뭘 해야 할지 모르겠다.

C#만의 독특한 구조는 분명 재미있었다. 이제 C++로 돌아갈 시간이다.