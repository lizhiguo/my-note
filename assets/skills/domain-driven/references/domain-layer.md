# 领域层代码模板

> 用于 **apply** 阶段生成领域层代码。开发顺序中最先创建。

---

## 1.1 Entities.kt

**职责**：聚合根 + 聚合内实体。封装业务规则和状态转换，发布领域事件。

**关键点**：
- 继承 `AbstractAuditableJpaEntity<E, ID>`（普通）或 `AbstractAuditableJpaTreeEntity`（树形）
- 标注 `@Audited` 启用 Envers 审计表
- 聚合根标注 `@AggregateRoot`；聚合内实体不标注
- **标识符必须写在实体内部**，定义为嵌套的 `@Embeddable` data class
- ID 使用雪花算法生成（`SnowflakeGeneratorHelper.generate()`）
- 提供 `create()` 工厂方法，不暴露构造函数
- 领域方法封装业务规则（`modify()`、`changeStatus()`、`addItem()`）
- 使用 `registerEvent()` 发布领域事件 — **严禁自定义事件管理代码**。`BaseEntity` 已继承 `AbstractAggregateRoot`，提供 `protected fun registerEvent(event)` + `@DomainEvents` + `@AfterDomainEventPublication`。不要写自己的 `_events` 列表、`private fun registerEvent()` 或 `releaseEvents()`——这些会遮蔽父类实现，导致 Spring Data 永远收不到事件
- 不暴露 setter，不调用 Repository，不依赖 Command/VO

```kotlin
package com.erke.biz.<module>.domain.model

import com.erke.common.data.jpa.model.entity.AbstractAuditableJpaEntity
import org.jmolecules.ddd.types.Identifier
import com.erke.common.core.helper.SnowflakeGeneratorHelper
import io.swagger.v3.oas.annotations.media.Schema
import jakarta.persistence.*
import org.hibernate.annotations.*
import org.hibernate.envers.Audited
import org.jmolecules.ddd.annotation.AggregateRoot
import java.io.Serializable

@Audited
@Entity
@DynamicInsert
@DynamicUpdate
@Table(name = "<table_name>", comment = "<table_comment>")
@AggregateRoot
class <Entity>(
    @EmbeddedId
    override var id: <Entity>Id? = null,

    @Column(name = "<col>", nullable = false, length = 50, comment = "<comment>")
    var <field>: String? = null,

    @Column(name = "status", nullable = false, length = 20, comment = "状态")
    @Convert(converter = <Entity>StatusConverter::class)
    var status: <Entity>Status? = <Entity>Status.DRAFT,

    @OneToMany(mappedBy = "<parent_ref>", cascade = [CascadeType.ALL], orphanRemoval = true)
    var items: MutableList<<ChildEntity>> = mutableListOf()

) : AbstractAuditableJpaEntity<<Entity>, <Entity>.<Entity>Id>() {

    @Embeddable
    data class <Entity>Id(
        @Column(name = "id", length = 19)
        @Schema(description = "主键值")
        val value: Long = SnowflakeGeneratorHelper.generate()
    ) : Identifier, Serializable

    companion object {
        fun create(attr: <Entity>Attr): <Entity> {
            val entity = attr.to<Entity>()
            entity.registerEvent(<Entity>Event.<Entity>Created(entityId = entity.id!!.value))
            return entity
        }
    }

    fun modify(attr: <Entity>Attr) {
        attr.updateEntity(this)
        registerEvent(<Entity>Event.<Entity>Modified(entityId = this.id!!.value))
    }

    fun changeStatus(newStatus: <Entity>Status) {
        require(this.status?.canTransitionTo(newStatus) == true) {
            "当前状态 [${status?.description}] 不允许变更为 [${newStatus.description}]"
        }
        this.status = newStatus
        registerEvent(<Entity>Event.<Entity>StatusChanged(entityId = this.id!!.value, status = newStatus))
    }
}
```

**聚合内实体**（继承 `AbstractAuditableJpaEntity`，不标注 `@AggregateRoot`，标注 `@Audited`）：

```kotlin
@Audited
@Entity
@DynamicInsert
@DynamicUpdate
@Table(name = "<child_table>", comment = "<comment>")
class <ChildEntity>(
    @EmbeddedId
    var id: <ChildEntity>Id? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "<parent_fk>", nullable = false, insertable = false, updatable = false)
    var <parent>: <Entity>? = null,

    @Column(name = "<col>", nullable = false)
    var <field>: String? = null,

    @Column(name = "status", nullable = false, length = 10)
    @Convert(converter = ItemStatusConverter::class)
    var status: ItemStatus = ItemStatus.ENABLED

) : AbstractAuditableJpaEntity<<ChildEntity>, <ChildEntity>.<ChildEntity>Id>() {

    @Embeddable
    data class <ChildEntity>Id(
        @Column(name = "id", length = 19)
        val value: Long = SnowflakeGeneratorHelper.generate()
    ) : Identifier, Serializable

    fun update(attr: <ChildEntity>Attr) {
        attr.<field>?.let { <field> = it }
    }
}
```

---

## 1.2 Inputs.kt

**职责**：领域层输入数据对象（Attr），与应用层解耦；提供 `toEntity()` / `updateEntity()` 扩展函数。

**关键点**：
- 字段全部使用可空类型，支持部分更新
- 不依赖 Command 或 VO
- 扩展函数定义在同文件

```kotlin
package com.erke.biz.<module>.domain.model

data class <Entity>Attr(
    val <field1>: String? = null,
    val <field2>: String? = null,
    val status: String? = null
)

fun <Entity>Attr.to<Entity>(): <Entity> {
    return <Entity>().also {
        it.<field1> = this.<field1>
        it.<field2> = this.<field2>
        it.status = this.status?.let { s -> <Entity>Status.fromCode(s) }
    }
}

fun <Entity>Attr.updateEntity(entity: <Entity>) {
    this.<field1>?.let { entity.<field1> = it }
    this.<field2>?.let { entity.<field2> = it }
    this.status?.let { entity.status = <Entity>Status.fromCode(it) }
}
```

---

## 1.3 ValueObjects.kt

**职责**：一个聚合根对应一个文件，集中定义所有值对象、枚举、枚举转换器。

**关键点**：
- 嵌入值对象：`@ValueObject` + `@Embeddable` data class，`init` 块校验
- 枚举值对象：`@ValueObject` enum class，提供 `fromCode()` + `@JsonCreator`
- 枚举转换器：继承 `AbstractEnumConverter`，`autoApply = true`
- 不要每个值对象单独建文件

```kotlin
package com.erke.biz.<module>.domain.model

import com.fasterxml.jackson.annotation.JsonCreator
import com.erke.common.data.jpa.converter.AbstractEnumConverter
import jakarta.persistence.Converter
import jakarta.persistence.Embeddable
import org.jmolecules.ddd.annotation.ValueObject

// ========== 嵌入值对象 ==========

@ValueObject
@Embeddable
data class <Entity>Code(val value: String) {
    init { require(value.isNotBlank()) { "<Entity>Code cannot be blank" } }

    companion object {
        fun of(value: String): <Entity>Code = <Entity>Code(value)
    }
}

// ========== 枚举值对象 ==========

@ValueObject
enum class <Entity>Status(val code: String, val description: String) {
    DRAFT("DRAFT", "起草"),
    ENABLED("ENABLED", "启用"),
    DISABLED("DISABLED", "停用"),
    DEPRECATED("DEPRECATED", "废弃");

    fun canTransitionTo(target: <Entity>Status): Boolean = when (this) {
        DRAFT -> target == ENABLED
        ENABLED -> target == DISABLED
        DISABLED -> target in listOf(ENABLED, DEPRECATED)
        DEPRECATED -> false
    }

    companion object {
        @JsonCreator @JvmStatic
        fun fromCode(code: String): <Entity>Status =
            entries.find { it.code == code }
                ?: throw IllegalArgumentException("Invalid <Entity>Status code: $code")
    }
}

// ========== 枚举转换器 ==========

@Converter(autoApply = true)
class <Entity>StatusConverter : AbstractEnumConverter<<Entity>Status, String>(
    <Entity>Status::class.java,
    { it.code },
    { <Entity>Status.fromCode(it) }
)
```

---

## 1.4 Repository.kt

**职责**：领域仓储接口（出站端口），只定义领域需要的特殊方法。

**关键点**：
- 继承 `IBaseDomainRepository<E, ID>`
- 标注 `@Repository`（DDD）+ `@SecondaryPort`
- 不包含查询方法（查询放 Dao）

```kotlin
package com.erke.biz.<module>.domain.repo

import com.erke.biz.<module>.domain.model.<Entity>
import com.erke.common.data.ddd.jpa.domain.repo.IBaseDomainRepository
import org.jmolecules.architecture.hexagonal.SecondaryPort
import org.jmolecules.ddd.annotation.Repository
import org.springframework.data.jpa.domain.Specification

@Repository
@SecondaryPort
interface <Entity>Repository : IBaseDomainRepository<<Entity>, <Entity>.<Entity>Id> {
    fun exists(spec: Specification<<Entity>>): Boolean
}
```

---

## 1.5 DomainService.kt

**职责**：领域服务是聚合根的"护法"——封装跨聚合/跨字段的业务规则校验，所有涉及 Repository 的条件查询（存在性检查、唯一性校验、数量统计等）都必须在此集中管理。**强制使用 Spec DSL 构建查询条件，严禁在 CommandHandler 中直接拼 Specification。**

**领域服务三件事（只能做这三件）**：
1. **按 ID 查询聚合根**：`getXxx(id)` — 不存在则抛业务异常
   - **探索期可省略**：仅当该模块无跨聚合校验时省略；出现第 2 个聚合后必须补齐
2. **业务规则校验**：唯一性、数量上限、状态前置条件等，使用 Spec DSL 构建条件
   - **探索期可延后**：业务规则未确定时不写 Spec DSL，宁可先不加校验也不要猜错
3. **返回领域数据**：给 CommandHandler 提供聚合根实例，本身不做保存

**领域服务三不碰（碰了就是违规）**：
- ❌ 不调用任何持久化写操作 — `repository.save()` / `saveAll()` / `delete()` / `deleteAll()` / `flush()` 一律禁止，保存和删除统一由 CommandHandler 负责
- ❌ 不调用 Dao / Mapper — 读操作走 Query 通道
- ❌ 不依赖 Command / VO / DTO — 只接受领域类型（Attr、值对象、基本类型）

**关键点**：
- 标注 `@Service`（Spring 依赖注入），只注入 `Repository`
- 使用 `BizException.of(ErrorCode, args)` 抛出业务异常
- **【强制】Spec DSL object 必须定义在同文件**，命名为 `<Entity>Spec`
- **【强制】所有数据库条件查询（exists / count / find）必须经过 Spec object**，不得在方法内直接拼接 `Specification`
- Spec 方法使用 Kotlin 扩展函数风格
- 使用 `com.erke.common.data.jpa.helper` 中的 `and()` / `or()` / `equal()` / `notEqual()` 等 DSL

```kotlin
package com.erke.biz.<module>.domain.service

import com.erke.biz.<module>.domain.exception.<Entity>ErrorCode
import com.erke.biz.<module>.domain.model.<Entity>
import com.erke.biz.<module>.domain.repo.<Entity>Repository
import com.erke.common.data.jpa.helper.*
import com.erke.common.core.exception.BizException
import org.springframework.stereotype.Service

@Service
class <Entity>DomainService(private val repository: <Entity>Repository) {

    // ========== 按 ID 查询 ==========

    fun get<Entity>(id: <Entity>.<Entity>Id): <Entity> =
        repository.findByIdOrNull(id)
            ?: throw BizException.of(<Entity>ErrorCode.<ENTITY>_NOT_FOUND, id)

    // ========== 业务规则校验 ==========

    fun validate<Field>Uniqueness(<field>: String?, excludeId: <Entity>.<Entity>Id? = null) {
        if (<field> == null) return
        if (repository.exists(<Entity>Spec.uniqueCheck(<field>, excludeId))) {
            throw BizException.of(<Entity>ErrorCode.<ENTITY>_<FIELD>_DUPLICATE, <field>)
        }
    }

    fun validateCountLimit(category: <Entity>Status, maxCount: Int = 200) {
        if (repository.count(<Entity>Spec.byStatus(category)) >= maxCount) {
            throw BizException.of(<Entity>ErrorCode.<ENTITY>_COUNT_LIMIT_EXCEEDED, maxCount)
        }
    }
}

// ========== Spec DSL（强制，必须定义）==========

object <Entity>Spec {
    fun uniqueCheck(<field>: String?, excludeId: <Entity>.<Entity>Id?): Specification<<Entity>> {
        val byField = <field>?.let { <Entity>::<field>.equal(it) }
        val excludeSelf = excludeId?.let { <Entity>::id.notEqual(it) }
        return and(excludeSelf, byField)
    }

    fun byStatus(status: <Entity>Status): Specification<<Entity>> =
        <Entity>::status.equal(status.code)

    fun byCategory(category: String): Specification<<Entity>> =
        <Entity>::category.equal(category)
}
```

**Spec DSL 常见模式**：

```kotlin
// 单条件精确匹配
fun byCode(code: String) = <Entity>::code.equal(code)

// 模糊匹配
fun byNameLike(name: String) = <Entity>::name.like("%$name%")

// 多条件 AND 组合
fun byCategoryAndStatus(category: String, status: String): Specification<<Entity>> =
    and(<Entity>::category.equal(category), <Entity>::status.equal(status))

// 排除自身 + 条件组合（唯一性校验专用）
fun uniqueCheck(code: String?, excludeId: <Entity>.<Entity>Id?): Specification<<Entity>> {
    val byCode = code?.let { <Entity>::code.equal(it) }
    val excludeSelf = excludeId?.let { <Entity>::id.notEqual(it) }
    return and(excludeSelf, byCode)
}

// 区间查询
fun byCreateTimeBetween(start: LocalDateTime, end: LocalDateTime): Specification<<Entity>> =
    <Entity>::createTime.between(start, end)
```

**DomainService 反模式（代码审查时直接打回）**：
```kotlin
// ❌ 错误：在方法内直接拼 Specification（不经过 Spec object）
fun validateCode(code: String) {
    val spec = Specification<<Entity>> { root, _, cb ->
        cb.equal(root.get<String>("code"), code)
    }
    if (repository.exists(spec)) throw ...
}

// ❌ 错误：在手写 repository 方法中拼条件
fun validateCode(code: String) {
    if (repository.existsByCode(code)) throw ...
}

// ✅ 正确：经过 Spec object
fun validateCode(code: String) {
    if (repository.exists(<Entity>Spec.byCode(code))) throw ...
}
```

---

## 1.6 Events.kt

**职责**：定义领域事件，使用 sealed class 封装。

**关键点**：
- 继承 `AbstractDomainEvent()`
- 标注 `@DomainEvent`（注意不是 `@ApplicationEvent`）
- 携带 `entityId`，不携带大量数据

```kotlin
package com.erke.biz.<module>.domain.event

import com.erke.common.core.model.AbstractDomainEvent
import org.jmolecules.event.annotation.DomainEvent

@DomainEvent(namespace = "<module>.<entity>")
sealed class <Entity>Event : AbstractDomainEvent() {

    @DomainEvent(namespace = "<module>.<entity>", name = "created")
    data class <Entity>Created(val entityId: Long) : <Entity>Event()

    @DomainEvent(namespace = "<module>.<entity>", name = "modified")
    data class <Entity>Modified(val entityId: Long) : <Entity>Event()

    @DomainEvent(namespace = "<module>.<entity>", name = "deleted")
    data class <Entity>Deleted(val entityId: Long) : <Entity>Event()
}
```

---

## 1.7 ErrorCode.kt

**职责**：领域错误码枚举。

**关键点**：
- 实现 `IBaseErrorCode`
- `code` 格式：`<PREFIX>_0001`
- `msg` 支持 `{0}` 占位符

```kotlin
package com.erke.biz.<module>.domain.exception

import com.erke.common.core.model.IBaseErrorCode

enum class <Entity>ErrorCode(override val code: String, override val msg: String) : IBaseErrorCode {
    <ENTITY>_NOT_FOUND("<PREFIX>_0001", "<实体>[{0}]不存在"),
    <ENTITY>_<FIELD>_DUPLICATE("<PREFIX>_0002", "<字段>[{0}]已存在"),
    <ENTITY>_STATUS_NOT_ALLOWED("<PREFIX>_0003", "当前状态不允许此操作");

    companion object {
        private val codeMap = entries.associateBy { it.code }
        fun byCode(code: String) = codeMap[code]
    }
}
```
