# Chief Summary — Integration Tests

## Work Item

integration-tests — 项目集成测试补充

## Current State

NEW

## Goal

制定并实现端到端集成测试，覆盖多模块协作场景

## Current Test Coverage

| 类型 | 状态 | 说明 |
|---|---|---|
| 后端单元测试 | ✅ 202 tests | analyzer、casebase、retrieval、core 模块 |
| API 路由测试 | ✅ 部分 | test_source_api、test_main（使用 TestClient） |
| 前端测试 | ✅ 33 tests | Vitest + @testing-library + msw |
| **集成测试** | ❌ 缺失 | 端到端多模块协作场景未覆盖 |

## Identified Integration Gaps

### 1. Full Scan Workflow
```
scanner.scan_directory → evidence.generate → report.generate
```
当前各模块独立测试，但全流程未串起来。

### 2. Case Lifecycle API
```
POST /api/cases → 写 case.md + metadata.yaml → 更新 index.yaml → GET /api/cases
```
当前只测了 POST，未验证完整生命周期。

### 3. Analysis Task Pipeline
```
scan → parse → classify → sample → timeline → evidence → case_draft
```
完整的日志分析流水线未端到端测试。

### 4. Diagnosis Workflow
```
task output → orchestrator → retrieval query → similar cases → LLM call
```
当前 diagnosis 有单元测试，但依赖真实文件系统的集成测试缺失。

## Next Action

solution-designer 设计集成测试方案
