# 천외마경II 卍MARU (ATMJ) — 한글 통합 패치

NDS 게임 **천외마경II 卍MARU** (Japan, 게임코드 ATMJ, 128 MiB) 의
**대사 + 메뉴 이미지** 를 한 번에 한글로 패치하는 패키지입니다.

이 한 패키지로 아래 두 가지가 **순서대로 한꺼번에** 적용됩니다.

1. **대사 / 폰트** — 전 스토리·엔딩·전투·시스템 UI·사운드 테스트 등 본문 대사 전체
   + 한글 폰트 + 시스템/전투/저장 텍스트. *(메뉴 그래픽은 건드리지 않음)*
2. **메뉴 이미지** — 메인/필드/하단 라벨 메뉴, 전투 명령 16개, 시작 선택 화면(起=처음 / 転=계속).
   `menu/png/` 안의 한글 PNG를 그대로 삽입하는 방식입니다.

> 서브로케이션명(지역 내 세부 지명, `chimei.scs`)은 별도 커스텀 글리프가 필요해
> 이번 패치에는 포함되지 않습니다(게임 진행·전투·메뉴에는 영향 없음).

---

## 준비물

- **Python 3.8 이상**
- 파이썬 패키지 **numpy, pillow, ndspy**
  ```
  pip install numpy pillow ndspy
  ```
- 천외마경II 卍MARU **(Japan, ATMJ) 롬 파일**. *이 패키지에는 롬이 들어있지 않습니다.*

---

## 사용법

### Windows
- **방법 1 (제일 쉬움)**: `patch_windows.bat` 위로 **롬 파일을 마우스로 끌어다 놓기**.
  → 같은 폴더에 `입력이름_KR.nds` 가 생깁니다.
- **방법 2**: 명령 프롬프트에서
  ```
  python patch.py 입력롬.nds 출력롬.nds
  ```

### Mac / Linux
```
chmod +x patch_mac_linux.sh        # 최초 1회
./patch_mac_linux.sh 입력롬.nds      # → 입력이름_KR.nds 로 저장
# 또는
python3 patch.py 입력롬.nds 출력롬.nds
```

패치가 끝나면 출력 `.nds` 를 에뮬레이터(멜론DS / DeSmuME)나 플래시카트에 올려 확인하세요.
정상 출력 크기는 **134,217,728 바이트(128 MiB)** 입니다.

---

## 입력 롬에 대해

- **원본 일본어 롬**, 또는 **이미 일부 패치한 롬** 어느 쪽이든 입력으로 쓸 수 있습니다.
- 가능하면 **매번 깨끗한 입력 롬**에 적용하세요. 같은 출력 파일에 반복해서 얹으면
  파일이 불필요하게 커질 수 있습니다(동작에는 무해).
- 이미 한글 메뉴/시스템 텍스트가 들어간 롬을 입력으로 주면, 대사 단계에서
  "원문 불일치" 경고가 다수 나올 수 있는데 이는 **기존 한글이 보존된다는 의미**라 정상입니다.

---

## 메뉴 이미지 직접 수정하기 (PNG 추출 → 편집 → 삽입)

메뉴 그래픽은 글꼴로 자동으로 그리지 않고, **PNG 이미지를 직접 만들어 넣는 방식**입니다.
`menu/png/` 안의 PNG가 그대로 롬에 들어가므로 원하는 모양으로 자유롭게 그릴 수 있습니다.

**기본 제공된 `menu/png/`** 에는 현재 한글 메뉴가 이미 들어 있어, 따로 손대지 않아도
`patch.py` 만 돌리면 그대로 적용됩니다. 직접 다시 그리고 싶을 때만 아래 과정을 따르세요.

### 1) 원본을 PNG로 추출
```
cd menu
python menu_extract.py 원본롬.nds png/
```
- **일본어 원본 롬**을 주면 일본어 원본 메뉴가 PNG로 나옵니다(밑그림으로 삼아 편집).
- 산출물:
  - `mainmenu.png` — 메인/필드/하단 라벨 등 (256×192, 팔레트 224색)
  - `command_01.png` ~ `command_17.png` — 전투 명령 아이콘 (각 32×16)
  - `kiten.png` — 시작 선택 화면 (256×256)
  - `_palette_mainmenu.png` / `_palette_command.png` — 색상표(참고용, 삽입 안 함)

### 2) PNG 편집 — 색과 크기를 지킬 것
이미지 편집기로 글자를 한글로 바꿉니다.

- **캔버스 크기(가로·세로)는 절대 바꾸지 마세요.**
- **원본에 쓰인 색(팔레트)만 사용하세요.**
  - `command_NN.png` : 검정(배경) · 흰색(글자) **2색만** 사용.
  - `mainmenu.png` / `kiten.png` : `_palette_*.png` 의 색상 안에서 사용하고,
    글자색·테두리색은 원본과 같은 색으로 칠하세요.
- 일부만 고쳐도 됩니다. `png/` 에 있는 PNG만 적용됩니다.

> 팁: 인덱스(P) 모드 그대로 편집하면 색이 정확히 보존됩니다.
> RGB로 칠해도 가장 가까운 팔레트 색으로 자동 매칭되지만, 원본 색을 그대로 쓰는 편이 안전합니다.

### 3) 삽입
```
python menu_insert.py 입력롬.nds png/ 출력롬.nds      # 메뉴만
```
또는 루트에서 **대사까지 한꺼번에**:
```
python patch.py 입력롬.nds 출력롬.nds                 # 2단계에서 menu/png/ 자동 삽입
```

---

## 폴더 구성

```
patch.py              ← 통합 러너 (이걸 실행)
patch_windows.bat     Windows 드래그앤드롭 실행
patch_mac_linux.sh    Mac/Linux 실행
banner_tool.py        지명 배너 프레임 너비 조절 도구 (부록 참고)
README.md             이 문서
LICENSE.txt           갈무리11 폰트 라이선스 (SIL OFL 1.1)

dialogue/             대사 + 폰트 패치 (메뉴 그래픽 제외)
  build_ko.py 외 스크립트, translation.json, ks2350.txt,
  arm9_translation.json, overlay_translation.json, Galmuri11.bdf

menu/                 메뉴 이미지 패치 키트 (PNG 추출/삽입)
  menu_extract.py     원본 메뉴 → PNG 추출
  menu_insert.py      수정한 PNG → 롬 삽입
  patch_all.py        png/ 의 PNG 일괄 삽입 (patch.py가 호출)
  png/                삽입할 한글 메뉴 PNG들  ← 이걸 수정
  tools.py, cmp.py    내부 라이브러리 (FAT/압축)
  PATCH_DATA.md       메뉴 바이너리 포맷 기술 사양
```

---

## 동작 방식 (요약)

1. `dialogue/build_ko.py --no-menu` 가 입력 롬을 받아
   - 폰트(한자 글리프 슬롯)에 한글 2,350자를 그려 넣고,
   - `translation.json` 의 번역된 대사로 모든 `.scs` 를 재조립하고,
   - 시스템/전투/저장 텍스트(ARM9·오버레이)를 한글로 바꿉니다(메뉴 그래픽은 제외).
2. `menu/patch_all.py` 가 그 결과 위에 `menu/png/` 안의 한글 메뉴 PNG들을
   삽입해 메뉴 그래픽(메인/필드/전투/시작 화면)을 덮어씁니다.

두 단계 모두 롬의 빈 패딩 영역에 데이터를 추가하고 FAT만 갱신하므로 헤더는 손상되지 않습니다.

---

## 글꼴 라이선스
- **Galmuri11** (대사 폰트) — SIL Open Font License 1.1 (`LICENSE.txt`).
- 메뉴 이미지 패치의 자세한 기술 사양은 `menu/PATCH_DATA.md` 참고.

---

## 부록: 지명 배너 프레임 너비 조절 (banner_tool.py)

지명 배너의 테두리 판은 **가장 넓은 행의 글자 수에 맞춰 자동으로 늘어납니다**
(가로 너비를 정하는 별도 코드는 없음). 헤더 `16 00 [p1] 00 [p2] 00` 의
p1 은 세로 레이아웃(5=후리가나행 있음 / 8=없음), p2=8 은 박스 높이로, 둘 다 가로와 무관합니다.

테두리를 넓히/좁히려면 **행 텍스트에 전각 공백 `　`(U+3000)** 을 넣어 글자 폭을 바꾸면 됩니다.

```
python banner_tool.py list                 # 모든 지명 배너 + 현재 프레임 너비
python banner_tool.py list 아키바            # 이름으로 검색
python banner_tool.py pad <인덱스> <목표너비>  # 본문 행을 좌우 균등 패딩해 너비 맞춤
python banner_tool.py setrow <인덱스> <행> "텍스트"   # 특정 행 직접 지정
```

- 이 도구는 `dialogue/translation.json` 을 자동 백업(.bak) 후 수정합니다.
- 수정한 다음 **다시 `patch.py` 로 빌드**하면 바뀐 너비가 적용됩니다.
