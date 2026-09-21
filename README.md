# Navic SideStore / AltStore Source

Navic의 공식 GitHub Release를 추적해 `source.json`을 자동으로 갱신하는 비공식 소스입니다. IPA 파일은 복사하거나 재배포하지 않고, 항상 Navic 원본 GitHub Release의 `Navic.ipa`를 가리킵니다.

## 동작 방식

- 6시간마다, 또는 Actions 화면에서 수동 실행할 때 Navic의 공개 릴리스를 확인합니다.
- `v1.0.0-alphaNN` 형식의 가장 최신 릴리스에서 `Navic.ipa`를 찾습니다.
- 태그 `v1.0.0-alpha55`는 IPA 내부 값에 맞춰 `version: 1.0.0`, `buildVersion: 55`로 기록합니다.
- 새 빌드가 있으면 `versions` 배열의 맨 앞에 추가하고 `source.json`만 커밋합니다.
- 최신 빌드가 이미 있으면 파일을 수정하지 않으므로 커밋도 만들지 않습니다.

## 설치

1. 이 저장소의 파일을 새 **공개 GitHub 저장소**에 올립니다.
2. 저장소의 **Settings → Actions → General → Workflow permissions**에서 **Read and write permissions**를 선택하고 저장합니다.
3. **Actions → Update Navic source → Run workflow**를 한 번 실행해 정상 동작을 확인합니다.
4. 아래 주소에서 `YOUR_GITHUB_USERNAME`과 `YOUR_REPOSITORY`를 실제 값으로 바꿉니다.

   ```text
   https://raw.githubusercontent.com/10000Je/navic-sidestore-source/main/source.json
   ```

5. 완성된 URL을 SideStore 또는 AltStore의 소스 주소로 추가합니다.

기본 브랜치가 `main`이 아니라면 URL의 `main`도 실제 기본 브랜치 이름으로 바꾸세요.

## 수동 실행

Python 3.9 이상에서 외부 패키지 없이 실행할 수 있습니다.

```bash
python scripts/update_source.py
```

스크립트는 `GITHUB_TOKEN` 환경 변수가 있으면 GitHub API 인증에 사용하고, 없으면 공개 API를 익명으로 호출합니다.

## 자동화 주기와 비용

워크플로는 UTC 기준 매 6시간의 17분에 실행됩니다. 표준 `ubuntu-latest` runner에서 API 호출 한 번과 작은 JSON 파일 처리만 수행합니다. 공개 저장소의 표준 GitHub-hosted runner는 무료로 사용할 수 있습니다.

GitHub는 공개 저장소에 60일간 활동이 없으면 예약 워크플로를 자동 비활성화할 수 있습니다. 그런 경우 Actions 화면에서 워크플로를 다시 활성화하거나 수동 실행하면 됩니다.

## 버전 매핑

AltStore 계열은 `version`과 `buildVersion`이 IPA의 `Info.plist` 값과 정확히 일치하기를 요구합니다.

| Navic 릴리스 태그 | `version` | `buildVersion` |
|---|---:|---:|
| `v1.0.0-alpha54` | `1.0.0` | `54` |
| `v1.0.0-alpha55` | `1.0.0` | `55` |

`marketingVersion`에는 사람이 보기 쉬운 `1.0.0-alphaNN`을 별도로 기록합니다.

## 참고 및 면책

이 저장소는 Navic 프로젝트와 공식적으로 연계되지 않은 커뮤니티용 자동화입니다. 앱과 IPA의 저작권 및 라이선스는 [Navic 원본 저장소](https://github.com/ssalggnikool/Navic)를 따릅니다. 이 저장소의 자동화 코드에는 MIT License가 적용됩니다.
