# 适配器层代码模板

> 用于 **apply** 阶段生成适配器层代码。最后创建。

---

## 3.1 Controller.kt

**职责**：接收 HTTP 请求，调用 UseCase/QueryCase，不含业务逻辑。

**关键点**：
- 标注 `@PrimaryAdapter` + `@Tag(name = "模块名", description = "功能描述")`
- 每个方法标注 `@Operation(summary, description)` + `@ApiResponses`
- `@PathVariable` / `@RequestParam` 标注 `@Parameter(description, required, example)`
- 只注入 `UseCase` 和 `QueryCase`，不注入 Repository 或 DomainService
- VO 通过 `RestAssembler` 的扩展函数转换为 Command

**Swagger 注解规范**：
- `@Tag` — 类级别，name 用中文业务名，description 一句话概括职责
- `@Operation` — 方法级别，summary 简短动词短语，description 补充业务规则
- `@ApiResponses` — 列出所有可能的 HTTP 状态码及其含义（200/201/204/400/404）
- `@Parameter` — 参数级别，description + required + example

```kotlin
package com.erke.biz.<module>.adapter.`in`.rest

import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.Parameter
import io.swagger.v3.oas.annotations.responses.ApiResponse
import io.swagger.v3.oas.annotations.responses.ApiResponses
import io.swagger.v3.oas.annotations.tags.Tag
import jakarta.validation.Valid
import org.jmolecules.architecture.hexagonal.PrimaryAdapter
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*

@Tag(name = "<模块中文名>", description = "<一句话职责描述>")
@RestController
@RequestMapping("/api/v1/<resources>")
@PrimaryAdapter
class <Entity>Controller(
    private val useCase: <Entity>UseCase,
    private val queryCase: <Entity>QueryCase
) {

    @Operation(summary = "新增<实体>", description = "<业务规则简述>")
    @ApiResponses(value = [
        ApiResponse(responseCode = "201", description = "创建成功"),
        ApiResponse(responseCode = "400", description = "<校验失败场景>")
    ])
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @RequestBody @Valid vo: <Entity>CreateVO
    ): <Entity>DTO = useCase.handle(vo.toCommand())

    @Operation(summary = "编辑<实体>", description = "<业务规则简述>")
    @ApiResponses(value = [
        ApiResponse(responseCode = "200", description = "修改成功"),
        ApiResponse(responseCode = "400", description = "<校验失败场景>"),
        ApiResponse(responseCode = "404", description = "实体不存在")
    ])
    @PutMapping("/{id}")
    fun update(
        @Parameter(description = "实体 ID", required = true) @PathVariable id: Long,
        @RequestBody @Valid vo: <Entity>UpdateVO
    ): <Entity>DTO = useCase.handle(vo.toCommand(id))

    @Operation(summary = "删除<实体>", description = "<业务规则简述>")
    @ApiResponses(value = [
        ApiResponse(responseCode = "204", description = "删除成功"),
        ApiResponse(responseCode = "404", description = "实体不存在")
    ])
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    fun delete(
        @Parameter(description = "实体 ID", required = true) @PathVariable id: Long
    ) {
        useCase.handle(<Entity>Cmd.Delete(id))
    }

    @Operation(summary = "状态变更", description = "<状态机规则简述>")
    @ApiResponses(value = [
        ApiResponse(responseCode = "200", description = "状态变更成功"),
        ApiResponse(responseCode = "400", description = "当前状态不允许此操作"),
        ApiResponse(responseCode = "404", description = "实体不存在")
    ])
    @PatchMapping("/{id}/status")
    fun changeStatus(
        @Parameter(description = "实体 ID", required = true) @PathVariable id: Long,
        @Parameter(description = "目标状态码", required = true, example = "ENABLED") @RequestParam status: String
    ): <Entity>DTO = useCase.handle(<Entity>Cmd.ChangeStatus(id, status))

    @Operation(summary = "按 ID 查询<实体>", description = "返回单条记录，不存在时返回 null")
    @ApiResponses(value = [
        ApiResponse(responseCode = "200", description = "查询成功")
    ])
    @GetMapping("/{id}")
    fun get(
        @Parameter(description = "实体 ID", required = true) @PathVariable id: Long
    ): <Entity>View? = queryCase.handle(<Entity>Query.GetQuery(id))

    @Operation(summary = "列表查询<实体>", description = "<筛选条件说明>")
    @ApiResponses(value = [
        ApiResponse(responseCode = "200", description = "查询成功，无数据时返回空列表")
    ])
    @GetMapping
    fun list(
        @Parameter(description = "<筛选条件>", example = "<示例值>") @RequestParam <param>: String
    ): List<<Entity>View>? = queryCase.handle(<Entity>Query.ListQuery(<filter>))
}
```

---

## 3.2 RestAssembler.kt

**职责**：VO → Command 扩展函数，集中在适配器层。

```kotlin
package com.erke.biz.<module>.adapter.`in`.rest

import com.erke.biz.<module>.api.model.*
import com.erke.biz.<module>.app.command.<Entity>Cmd

fun <Entity>CreateVO.toCommand(): <Entity>Cmd.Create =
    <Entity>Cmd.Create(<field1> = this.<field1>!!, <field2> = this.<field2>)

fun <Entity>UpdateVO.toCommand(id: Long): <Entity>Cmd.Modify =
    <Entity>Cmd.Modify(entityId = id, <field1> = this.<field1>)
```

---

## 3.3 JpaRepositories.kt

**职责**：JPA Repository 接口，继承基类，支持 Envers 审计。

```kotlin
@Repository
interface <Entity>JpaRepository :
    IBaseJpaRepository<<Entity>, <Entity>.<Entity>Id>,
    RevisionRepository<<Entity>, <Entity>.<Entity>Id, Long>
```

---

## 3.4 RepositoryAdapter.kt

**职责**：实现领域 Repository 接口，只做写操作。

**关键点**：
- 标注 `@SecondaryAdapter`
- 继承 `BaseJpaAdapter` 获得基础 CRUD
- 可用 `findByIdWithGraph` 加载关联实体

```kotlin
@SecondaryAdapter
@Repository
class <Entity>JpaAdapter(val repository: <Entity>JpaRepository) :
    BaseJpaAdapter<<Entity>, <Entity>.<Entity>Id, <Entity>JpaRepository>(repository),
    <Entity>Repository {

    override fun exists(spec: Specification<<Entity>>) = repository.exists(spec)

    override fun findByIdOrNull(id: <Entity>.<Entity>Id) =
        repository.findByIdWithGraph(id, listOf("<association>"))
}
```

---

## 3.5 Mappers.kt

**职责**：MyBatis Mapper 接口，只做读操作，返回 View 对象。
**强制规范**：**一个聚合根只能对应一个 Mapper 接口（Dao）和唯一一个 XML 文件**。即使涉及到聚合内实体的查询，也必须在这个聚合统一的 Mappers.kt 和与之对应的单个 XML 中定义。

```kotlin
@Mapper
interface <Entity>ReadMapper {
    fun selectById(@Param("id") id: Long): <Entity>View?
    fun selectListByFilter(@Param("filter") filter: <Entity>Filter): List<<Entity>View>
}
```

---

## 3.6 XxxMapper.xml

**文件位置**：`src/main/resources/mapper/<Entity>Mapper.xml`

**关键点**：
- **【强制】一个聚合根只能拥有一个 Mapper XML 文件**。严禁为聚合内实体单独创建 XML 文件。
- `namespace` 必须与 Mapper 接口全限定名一致
- `<select id>` 必须与 Mapper 接口方法名一致
- 使用 `<sql>` 提取公共字段，使用 `<resultMap>` 映射 View

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.erke.biz.<module>.adapter.out.read.mybatis.<Entity>ReadMapper">

    <sql id="baseColumns">
        id, <field1>, <field2>, status, create_time, update_time
    </sql>

    <resultMap id="<Entity>ViewMap" type="com.erke.biz.<module>.api.model.<Entity>View">
        <id property="id" column="id"/>
        <result property="<field1>" column="<field1>"/>
        <result property="status" column="status"/>
        <result property="createTime" column="create_time"/>
    </resultMap>

    <sql id="whereClause">
        <where>
            <if test="filter.<field1> != null and filter.<field1> != ''">
                AND <field1> LIKE CONCAT('%', #{filter.<field1>}, '%')
            </if>
            <if test="filter.status != null">
                AND status = #{filter.status}
            </if>
        </where>
    </sql>

    <select id="selectById" resultMap="<Entity>ViewMap">
        SELECT <include refid="baseColumns"/>
        FROM <table_name>
        WHERE id = #{id}
    </select>

    <select id="selectListByFilter" resultMap="<Entity>ViewMap">
        SELECT <include refid="baseColumns"/>
        FROM <table_name>
        <include refid="whereClause"/>
        ORDER BY create_time DESC
    </select>

</mapper>
```

---

## 3.7 DaoAdapter.kt

**职责**：实现应用层 Dao 接口，只做读操作，使用 PageHelper 分页。

```kotlin
@SecondaryAdapter
@Repository
class <Entity>DaoAdapter(val mapper: <Entity>ReadMapper) : <Entity>Dao {
    override fun findById(entityId: Long) = mapper.selectById(entityId)
    override fun findListByFilter(filter: <Entity>Filter) = mapper.selectListByFilter(filter)
    override fun findPageByFilter(filter: <Entity>Filter, pageNum: Int, pageSize: Int) =
        PageHelper.startPage<<Entity>View>(pageNum, pageSize)
            .doSelectPage { mapper.selectListByFilter(filter) }
            .toPageResult()
}
```
