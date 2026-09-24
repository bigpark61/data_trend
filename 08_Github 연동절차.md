## GitHub 연동 절차

### 1. Git 설치 확인

PowerShell에서 실행합니다.

```powershell
git --version
```

Git이 없다면 [Git 공식 사이트](https://git-scm.com/downloads)에서 설치합니다.

### 2. Git 사용자 정보 설정

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

설정 확인:

```powershell
git config --global --list
```

### 3. 프로젝트 폴더로 이동

```powershell
cd C:\Temp\data_trend
```

### 4. `.gitignore` 파일 생성

가상환경과 생성 결과물을 GitHub에 올리지 않도록 합니다.

```gitignore
.venv/
__pycache__/
*.pyc
output/
.env
```

### 5. Git 저장소 초기화

```powershell
git init
```

### 6. 파일 추가 및 첫 커밋

```powershell
git add .
git commit -m "Initial commit"
```

상태 확인:

```powershell
git status
```

### 7. GitHub에서 원격 저장소 생성

GitHub에서:

1. `New repository` 선택
2. 저장소 이름 입력  
   예: `ai-trend-dashboard`
3. 공개 여부 선택
4. `README`, `.gitignore`, License는 추가하지 않음
5. `Create repository` 클릭

### 8. 원격 저장소 연결

GitHub 저장소 주소를 사용합니다.

```powershell
git remote add origin https://github.com/USERNAME/ai-trend-dashboard.git
```

연결 확인:

```powershell
git remote -v
```

### 9. GitHub에 업로드

```powershell
git branch -M main
git push -u origin main
```

로그인 창이 나타나면 GitHub 계정으로 인증합니다. GitHub는 일반 비밀번호 대신 브라우저 인증이나 Personal Access Token을 사용할 수 있습니다.

### 10. 이후 변경사항 업로드

파일을 수정한 뒤 다음 명령을 반복합니다.

```powershell
git add .
git commit -m "Update dashboard"
git push
```

전체 흐름은 다음과 같습니다.

```text
로컬 프로젝트
  -> git init
  -> git add .
  -> git commit
  -> GitHub 저장소 연결
  -> git push
```

현재 프로젝트에서는 `.venv`와 `output`을 제외하고 Python 소스, CSV, HTML, README를 GitHub에 올리는 구성이 적절합니다.