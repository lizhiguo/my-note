# Erke 架构参考 - 六边形架构概述

> 用于 **propose / design.md** 阶段。在设计新功能时，必须先读本文件确认模块归属、调用链方向和分层边界。

---

## 1. 整体技术栈

| 关注点 | 技术选型 |
|--------|----------|
| 语言 | Kotlin 2.3.20 |
| 构建 | Maven（Multi-Module Project） |
| 架构 | DDD 六边形架构（jMolecules 注解） |
| 模块化 | Spring Modulith 2.0.5 |
| 写操作持久化 | JPA（Spring Data JPA + Hibernate Envers） |
| 读操作持久化 | MyBatis + PageHelper |
| 对象映射 | Kotlin 扩展函数（无 MapStruct） |
| Java 版本 | 21 |

---

## 2. 顶层目录结构

```
lhl/                              # 主项目（Maven Root POM）
├── lhl-bom/                      # 独立 BOM（依赖版本管理）
├── lhl-common/                   # 框架层
│   ├── lhl-common-bom/           # common 模块 BOM
│   ├── lhl-common-core/          # 通用基础：异常、BaseDTO、SnowflakeGeneratorHelper、AbstractDomainEvent
│   ├── lhl-common-data/
│   │   ├── common-data-jpa/       # JPA 增强：IBaseJpaRepository、AbstractAuditableJpaEntity、枚举转换、Spec DSL
│   │   └── common-data-mybatis/   # MyBatis 增强：分页转换扩展
│   └── lhl-common-ddd/
│   │   └── ddd-data-jpa/          # DDD 六边形基类：BaseJpaAdapter、IBaseDomainRepository、类型别名
│   └── lhl-starter/               # 自定义的boot
│   │   ├── api-starter/           # 对请求和响应数据的加工
│   │   └── jwt-starter/           # 使用jwt的加工
└── lhl-modules/                  # 业务模块
    └── lhl-demo/
        └── ddd-demo/              # 验证DDD的做法
```

**Maven 坐标**：`groupId = com.erke`

---

## 3. 框架层关键类速查

### 3.1 JPA 实体继承链

| 类 | 位置 | 说明 |
|----|------|------|
| `JpaEntity<ID>` | `common-data-jpa` / `com.erke.common.data.jpa.model.entity` | 顶层接口 |
| `BaseEntity<E, ID>` | 同上 | 抽象基类，`version` + `extJsonObject`，继承 `AbstractAggregateRoot` |
| `AbstractAuditableJpaEntity<E, ID>` | 同上 | 添加审计字段（createTime/updateTime/createBy/updateBy），标注 `@Audited` |
| `AbstractAuditableJpaTreeEntity<E, ID>` | 同上 | 树形结构版本，支持 parent/children |
| `IBaseJpaRepository<E, ID>` | 同上 / `repository` | JPA Repository 基础接口（extends `JpaRepository` + `JpaSpecificationExecutor` + `RevisionRepository`） |

### 3.2 DDD 六边形基类（`erke-common-ddd/ddd-data-jpa`）

| 类 | 位置 | 说明 |
|----|------|------|
| `IBaseDomainRepository<E, ID>` | `com.erke.common.data.ddd.jpa.domain.repo` | 领域仓储接口：`save()`、`delete()`、`findByIdOrNull()`、`existsById()` |
| `IDddJpaRepository<E, ID>` | 同上 | 继承 `IBaseJpaRepository` 的 DDD 版本 |
| `BaseJpaAdapter<E, ID, R>` | `com.erke.common.data.ddd.jpa.adapter` | 出站适配器抽象基类，实现 `IBaseDomainRepository` |

### 3.3 通用工具（`erke-common-core`）

| 类 | 说明 |
|----|------|
| `BizException` / `BizException.of(ErrorCode, args)` | 业务异常 |
| `AbstractDomainEvent` | 领域事件基类 |
| `BaseDTO` / `PageResult` | DTO 基类 / 分页结果 |
| `SnowflakeGeneratorHelper.generate()` | 雪花 ID 生成 |
| `AbstractEnumConverter` | JPA 枚举转换器基类 |

---

## 4. 领域模块六边形目录（每个模块的标准结构）

```
com.erke.biz.<module>/            # 业务模块基础包
├── api/                        # API 层（对外契约）
│   └── model/
│       ├── Vos.kt             # 请求 VO（HTTP 入参，纯 data class）
│       ├── Dtos.kt            # 写操作响应 DTO
│       ├── Filters.kt         # 查询条件（MyBatis 动态 SQL）
│       └── Views.kt           # 读操作响应 View（MyBatis 直接映射）
│
├── adapter/                    # 适配器层（六边形边界）
│   ├── in/
│   │   ├── rest/
│   │   │   ├── Controller.kt
│   │   │   └── RestAssembler.kt   # VO → Command 扩展函数
│   │   └── listener/internal/
│   │       └── EventListener.kt   # 跨模块事件监听
│   └── out/
│       ├── write/jpa/
│       │   ├── JpaRepositories.kt  # JPA 接口（继承 IBaseJpaRepository + RevisionRepository）
│       │   └── RepositoryAdapter.kt # 实现领域 Repository（继承 BaseJpaAdapter）
│       └── read/mybatis/
│           ├── Mappers.kt         # MyBatis Mapper 接口
│           ├── DaoAdapter.kt      # 实现应用层 Dao（使用 PageHelper 分页）
│           └── (resources) mapper/XxxMapper.xml  # SQL 映射文件
│
├── app/                        # 应用层（编排）
│   ├── command/
│   │   ├── Commands.kt        # 命令定义 + toAttr() 扩展函数
│   │   └── CommandHandler.kt  # 实现 UseCase，编排业务流程
│   ├── query/
│   │   ├── Queries.kt
│   │   └── QueryHandler.kt
│   ├── port/
│   │   ├── in/
│   │   │   ├── UseCase.kt        # 写操作入站端口（@PrimaryPort）
│   │   │   └── QueryCase.kt      # 读操作入站端口（@PrimaryPort）
│   │   └── out/
│   │       └── Dao.kt            # 读操作出站端口（@SecondaryPort）
│   └── helper/
│       └── AppAssembler.kt    # Entity → DTO 扩展函数
│
└── domain/                     # 领域层（核心，不依赖任何外层）
    ├── model/
    │   ├── Entities.kt        # 聚合根（@AggregateRoot）+ 聚合内实体
    │   ├── ValueObjects.kt    # 值对象 + 枚举 + 枚举转换器
    │   └── Inputs.kt          # Attr 数据类 + Attr→Entity 扩展函数
    ├── repo/Repository.kt     # 领域仓储接口（@Repository + @SecondaryPort）
    ├── service/DomainService.kt  # 领域服务 + Spec DSL
    ├── event/Events.kt        # 领域事件 sealed class
    └── exception/ErrorCode.kt # 错误码枚举（实现 IBaseErrorCode）
```

---

## 5. 六边形注解对照表

| 层级 | 文件 | 注解 | 角色 |
|------|------|------|------|
| adapter/in/rest | Controller.kt | `@PrimaryAdapter` | 入站适配器 |
| app/port/in | UseCase.kt / QueryCase.kt | `@PrimaryPort` | 入站端口（接口） |
| app/command | CommandHandler.kt | `@PrimaryAdapter` | 入站适配器（实现 UseCase） |
| app/query | QueryHandler.kt | `@PrimaryAdapter` | 入站适配器（实现 QueryCase） |
| app/port/out | Dao.kt | `@SecondaryPort` | 出站端口（接口） |
| domain/repo | Repository.kt | `@Repository` + `@SecondaryPort` | DDD 仓储 + 出站端口 |
| adapter/out/write | RepositoryAdapter.kt | `@SecondaryAdapter` | 写出站适配器（继承 BaseJpaAdapter） |
| adapter/out/read | DaoAdapter.kt | `@SecondaryAdapter` | 读出站适配器 |
| domain/model | Entities.kt 聚合根 | `@AggregateRoot` | DDD 聚合根 |

---

## 6. 调用链（必须严格遵守方向）

### 6.1 写操作调用链

```
HTTP 请求
  → Controller (@PrimaryAdapter)
      → RestAssembler.VO.toCommand()         # VO → Cmd
  → UseCase (@PrimaryPort)
  → CommandHandler (@PrimaryAdapter)
      → DomainService.validateXxx()          # 业务校验 → Spec.xxx() DSL
      → DomainService.getXxx(id)             # 按 ID 查聚合根（修改时）
      → Cmd.toAttr()                         # Cmd → Attr
      → Entity.create(attr) / entity.modify(attr)  # 领域方法
      → Repository.save(entity)             # @SecondaryPort
  → RepositoryAdapter (@SecondaryAdapter)    # 继承 BaseJpaAdapter
      → JpaRepositories（继承 IBaseJpaRepository）→ DB
  → entity.toDto()                          # Entity → DTO
  → 返回 DTO
```

### 6.2 读操作调用链

```
HTTP 请求
  → Controller (@PrimaryAdapter)
  → QueryCase (@PrimaryPort)
  → QueryHandler (@PrimaryAdapter)
      → Dao (@SecondaryPort)
  → DaoAdapter (@SecondaryAdapter)
      → MyBatis Mapper → DB
      → 直接映射为 View
  → 返回 View
```

### 6.3 跨模块事件调用链

```
CommandHandler
  → entity.registerEvent(XxxEvent.Created(...))
  → Spring Modulith 异步发布
  → EventListener (adapter/in/listener/internal/)
      → 调用其他模块的 UseCase
```

---

## 7. 数据对象职责速查

| 对象 | 所在层 | 用途 | 谁负责转换 |
|------|--------|------|------------|
| `XxxCreateVO / XxxUpdateVO` | api/model | HTTP 入参，纯 data class | RestAssembler（VO→Cmd） |
| `XxxCmd` | app/command | 写操作命令 | Commands.kt（Cmd→Attr） |
| `XxxAttr` | domain/model | 领域层输入 | Inputs.kt（Attr→Entity） |
| `Entity` | domain/model | 聚合根/实体（继承 AbstractAuditableJpaEntity） | AppAssembler（Entity→DTO） |
| `XxxDTO` | api/model | 写操作响应 | AppAssembler 扩展函数转换 |
| `XxxView` | api/model | 读操作响应 | MyBatis 直接映射 |
| `XxxFilter` | api/model | 查询条件 | 传入 MyBatis XML |
| `XxxQuery` | app/query | 读操作查询对象 | QueryHandler 构建 |

**转换函数链**：
```
VO.toCommand()  →  Cmd.toAttr()  →  Attr.toEntity()  →  Entity.toDto()
（RestAssembler）    （Commands.kt）    （Inputs.kt）       （AppAssembler）
```

---

## 8. 层间依赖禁止事项

| 禁止 | 正确做法 |
|------|----------|
| Controller 直接注入 Repository | Controller 只调用 UseCase / QueryCase |
| CommandHandler 直接访问 Dao | 读写分离，Handler 只用 Repository |
| 领域层依赖 Command/VO | 领域层只接受 Attr |
| QueryHandler 调用 Repository | QueryHandler 只调用 Dao |
| 在应用层定义业务规则 | 业务规则放在 Entity 或 DomainService |
| 使用 XxxService 命名服务类 | 用 CommandHandler / QueryHandler / DomainService |
| Repository 接口定义查询方法 | 查询方法放在 Dao 接口 |
| CommandHandler 中直接拼接 Specification | 经过 DomainService → Spec object |
| DomainService 调用持久化写操作（save/delete） | 保存和删除统一由 CommandHandler 负责 |
| DomainService 调用 Dao / Mapper | DomainService 只用 Repository（写通道） |
| 文件名带业务前缀（如 DictEntity.kt） | 使用固定规范名（Entities.kt、Repository.kt） |
