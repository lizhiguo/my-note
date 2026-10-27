# 应用层代码模板

> 用于 **apply** 阶段生成应用层代码。依赖领域层完成后创建。

---

## 2.1 Commands.kt

**职责**：写操作命令定义 + `toAttr()` 扩展函数。

**关键点**：
- sealed class 封装所有命令，标注 `@Command`
- 每个命令提供 `toAttr()` 扩展函数

```kotlin
package com.erke.biz.<module>.app.command

import org.jmolecules.architecture.cqrs.Command

@Command(namespace = "<module>.<entity>")
sealed class <Entity>Cmd {
    data class Create(val <field1>: String?, val <field2>: String?) : <Entity>Cmd()
    data class Modify(val entityId: Long, val <field1>: String? = null) : <Entity>Cmd()
    data class Delete(val entityId: Long) : <Entity>Cmd()
    data class ChangeStatus(val entityId: Long, val status: String) : <Entity>Cmd()
}

fun <Entity>Cmd.Create.toAttr() = <Entity>Attr(<field1> = <field1>, <field2> = <field2>)
fun <Entity>Cmd.Modify.toAttr() = <Entity>Attr(<field1> = <field1>)
```

---

## 2.2 UseCase.kt

**职责**：写操作入站端口接口。

**关键点**：
- 标注 `@PrimaryPort`
- 方法名统一用 `handle`，通过参数类型区分

```kotlin
package com.erke.biz.<module>.app.port.`in`

import com.erke.biz.<module>.api.model.<Entity>DTO
import com.erke.biz.<module>.app.command.<Entity>Cmd
import org.jmolecules.architecture.hexagonal.PrimaryPort

@PrimaryPort
interface <Entity>UseCase {
    fun handle(cmd: <Entity>Cmd.Create): <Entity>DTO
    fun handle(cmd: <Entity>Cmd.Modify): <Entity>DTO
    fun handle(cmd: <Entity>Cmd.Delete)
    fun handle(cmd: <Entity>Cmd.ChangeStatus): <Entity>DTO
}
```

---

## 2.3 CommandHandler.kt

**职责**：实现 UseCase，编排业务流程：校验 → 领域方法 → 保存。

**关键点**：
- 标注 `@PrimaryAdapter` + `@Component` + `@Transactional`
- 实现 `UseCase` 接口
- 调用顺序：domainService.validate → cmd.toAttr() → Entity.create/modify → repository.save

```kotlin
package com.erke.biz.<module>.app.command

import com.erke.biz.<module>.api.model.<Entity>DTO
import com.erke.biz.<module>.app.helper.toDto
import com.erke.biz.<module>.app.port.`in`.<Entity>UseCase
import com.erke.biz.<module>.domain.model.<Entity>
import com.erke.biz.<module>.domain.repo.<Entity>Repository
import com.erke.biz.<module>.domain.service.<Entity>DomainService
import org.jmolecules.architecture.hexagonal.PrimaryAdapter
import org.springframework.stereotype.Component
import org.springframework.transaction.annotation.Transactional

@PrimaryAdapter
@Component
@Transactional(rollbackFor = [Exception::class])
class <Entity>CommandHandler(
    private val repository: <Entity>Repository,
    private val domainService: <Entity>DomainService
) : <Entity>UseCase {

    override fun handle(cmd: <Entity>Cmd.Create): <Entity>DTO {
        domainService.validate<Field>Uniqueness(cmd.<field>, null)
        val entity = <Entity>.create(cmd.toAttr())
        repository.save(entity)
        return entity.toDto()
    }

    override fun handle(cmd: <Entity>Cmd.Modify): <Entity>DTO {
        val entityId = <Entity>.<Entity>Id(cmd.entityId)
        domainService.validate<Field>Uniqueness(cmd.<field>, entityId)
        val entity = domainService.get<Entity>(entityId)
        entity.modify(cmd.toAttr())
        repository.save(entity)
        return entity.toDto()
    }

    override fun handle(cmd: <Entity>Cmd.Delete) {
        val entity = domainService.get<Entity>(<Entity>.<Entity>Id(cmd.entityId))
        repository.delete(entity)
    }

    override fun handle(cmd: <Entity>Cmd.ChangeStatus): <Entity>DTO {
        val entity = domainService.get<Entity>(<Entity>.<Entity>Id(cmd.entityId))
        entity.changeStatus(<Entity>Status.fromCode(cmd.status))
        repository.save(entity)
        return entity.toDto()
    }
}
```

---

## 2.4 QueryCase / Queries / QueryHandler / Dao

```kotlin
// QueryCase.kt - 读操作入站端口
@PrimaryPort
interface <Entity>QueryCase {
    fun handle(query: <Entity>Query.GetQuery): <Entity>View?
    fun handle(query: <Entity>Query.ListQuery): List<<Entity>View>?
    fun handle(query: <Entity>Query.PageQuery): PageResult<<Entity>View>?
}

// Queries.kt - 查询对象
sealed class <Entity>Query {
    data class GetQuery(val entityId: Long) : <Entity>Query()
    data class ListQuery(val filter: <Entity>Filter) : <Entity>Query()
    data class PageQuery(val filter: <Entity>Filter, val pageNum: Int, val pageSize: Int) : <Entity>Query()
}

// Dao.kt - 读操作出站端口 (@SecondaryPort)
@SecondaryPort
interface <Entity>Dao {
    fun findById(entityId: Long): <Entity>View?
    fun findListByFilter(filter: <Entity>Filter): List<<Entity>View>?
    fun findPageByFilter(filter: <Entity>Filter, pageNum: Int, pageSize: Int): PageResult<<Entity>View>?
}

// QueryHandler.kt
@PrimaryAdapter
@Component
class <Entity>QueryHandler(private val dao: <Entity>Dao) : <Entity>QueryCase {
    override fun handle(query: <Entity>Query.GetQuery) = dao.findById(query.entityId)
    override fun handle(query: <Entity>Query.ListQuery) = dao.findListByFilter(query.filter)
    override fun handle(query: <Entity>Query.PageQuery) =
        dao.findPageByFilter(query.filter, query.pageNum, query.pageSize)
}
```

---

## 2.5 AppAssembler.kt

**职责**：Entity → DTO 扩展函数。

**关键点**：
- 使用 Kotlin 扩展函数，不使用 MapStruct
- 值对象字段需展开为简单类型
- 使用 `.also {}` 设置审计字段

```kotlin
package com.erke.biz.<module>.app.helper

import com.erke.biz.<module>.api.model.<Entity>DTO
import com.erke.biz.<module>.domain.model.<Entity>

fun <Entity>.toDto() = <Entity>DTO(
    id = id!!.value,
    <field1> = <field1>,
    status = status?.code
).also {
    it.version = version
    it.createBy = createBy
    it.createTime = createTime
    it.updateBy = updateBy
    it.updateTime = updateTime
}
```
