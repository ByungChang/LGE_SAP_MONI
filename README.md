# SAP AI Monitoring Supervisor

로컬에서는 Python 소스코드만 개발하고, Docker 이미지는 `AWS CodeBuild`에서 빌드해서 `ECR`에 올린 뒤 `ECS`가 사용하도록 구성하는 예제입니다.

## 구조

```text
app/
  api/alerts.py
  graph/supervisor.py
  models/alerts.py
  services/bedrock.py
  main.py
requirements.txt
Dockerfile
buildspec.yml
```

## 로컬 개발

Docker 없이 로컬에서 앱만 실행합니다.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

테스트 요청:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/alerts -ContentType "application/json" -Body '{
  "alert_id": "ALT-001",
  "title": "Dialog Response Time High",
  "severity": "high",
  "source": "SAP CCMS",
  "sid": "PRD",
  "client": "100",
  "host": "prd-app-01",
  "timestamp": "2026-04-23T10:15:00+09:00",
  "raw_message": "Average dialog response time exceeded threshold",
  "system_context": {
    "environment": "production",
    "business_service": "order_processing",
    "criticality": "mission_critical",
    "owner_team": "SAP Basis"
  }
}'
```

## CodeBuild 연동 개념

저장소에 `Dockerfile`과 `buildspec.yml`만 있으면, 로컬 Docker 없이도 CodeBuild가 아래를 수행합니다.

1. Python 코드 검증
2. Docker 이미지 빌드
3. ECR 푸시
4. `imagedefinitions.json` 생성

`imagedefinitions.json`은 이후 CodePipeline이나 ECS 배포 단계에서 새 이미지 태그를 반영할 때 사용합니다.

## CodeBuild 환경변수

CodeBuild 프로젝트에 아래 환경변수를 넣어주세요.

- `AWS_DEFAULT_REGION`: 예) `ap-northeast-2`
- `IMAGE_REPO_NAME`: 예) `sap-ai-supervisor`
- `ECS_CONTAINER_NAME`: ECS Task Definition의 container name과 동일한 값

## CodeBuild 서비스 역할 권한

최소 아래 권한이 필요합니다.

- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:CompleteLayerUpload`
- `ecr:InitiateLayerUpload`
- `ecr:PutImage`
- `ecr:UploadLayerPart`
- `ecr:BatchGetImage`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `s3:GetObject`
- `s3:PutObject`

## CodeBuild 프로젝트 생성 시 체크

- Environment image: `aws/codebuild/standard:7.0` 이상
- Privileged: `Enabled`
  `docker build`를 CodeBuild 안에서 수행하려면 이 옵션이 꼭 필요합니다.
- Source: GitHub / CodeCommit / Bitbucket 중 선택
- Buildspec: 저장소 루트의 `buildspec.yml`

## ECS 연동 방식

일반적으로는 아래 둘 중 하나입니다.

1. CodePipeline 사용
   Source -> CodeBuild -> ECS Deploy

2. CodeBuild 후 별도 배포 스텝
   ECR 푸시 후 수동 또는 스크립트로 ECS 서비스 재배포

운영에서는 보통 `CodePipeline + ECS`가 가장 깔끔합니다.
