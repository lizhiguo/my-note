# API 层代码模板

> 用于 **apply** 阶段生成 API 层代码。依赖领域层值对象完成后创建。

---

## 4.1 Vos.kt

**关键点**：请求 VO 不继承基类，纯 data class，`@Schema` 标注文档，Jakarta Validation 校验，类名后缀用大写 `VO`

```kotlin
@Schema(name = "创建<实体>请求")
data class <Entity>CreateVO(
    @field:Schema(description = "<字段>")
    @field:NotBlank(message = "<字段>不能为空")
    val <field>: String? = null
)
```

---

## 4.2 Dtos.kt

**关键点**：写操作响应，值对象展开为简单类型，包含审计字段，类名后缀用大写 `DTO`

```kotlin
@Schema(name = "<实体>响应")
data class <Entity>DTO(
    val id: Long?,
    val <field>: String?,
    val status: String?,
    var createTime: String? = null,
    var updateTime: String? = null
)
```

---

## 4.3 Filters.kt

**关键点**：字段全部可空，用于 MyBatis 动态条件，不含校验注解

```kotlin
data class <Entity>Filter(
    val <field>: String? = null,
    val status: String? = null
)
```

---

## 4.4 Views.kt

**关键点**：读操作响应，由 MyBatis 直接映射，可含描述性字段（如 `statusDesc`）

```kotlin
@Schema(name = "<实体>视图")
data class <Entity>View(
    val id: Long?,
    val <field>: String?,
    val status: String?,
    val statusDesc: String?
)
```
