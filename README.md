# McNemar's Test

1. data_preparation
   - 평가에 필요한 `samples` 파일(`.jsonl` | `.xlsx`)만 남기고 나머지 파일을 삭제
2. rename
   - 각 데이터셋의 `samples` 파일명을 표준 형식으로 통일
3. line_check
   - 데이터셋별 문항 수를 확인하여 누락이 없는지 검증
4. merge_data
   - 두 모델의 정답/오답 결과를 원본 데이터와 병합하여 분석용 통합 데이터를 생성