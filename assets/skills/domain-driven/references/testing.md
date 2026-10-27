# 测试代码模板

> 用于 **apply** 阶段编写测试代码。

---

## 5.1 领域实体测试（必须，覆盖率 ≥ 90%）

测试内容：create 工厂方法、领域方法（modify/changeStatus）、状态机、事件发布

```kotlin
class <Entity>Test {
    @Test
    fun `create should generate id and register event`() {
        val entity = <Entity>.create(<Entity>Attr(<field> = "test"))
        assertNotNull(entity.id)
        assertTrue(entity.domainEvents().first() is <Entity>Event.<Entity>Created)
    }

    @Test
    fun `changeStatus should fail when transition not allowed`() {
        val entity = <Entity>.create(...)
        assertThrows<IllegalArgumentException> { entity.changeStatus(<Entity>Status.DISABLED) }
    }
}
```

---

## 5.2 领域服务测试（必须，覆盖率 ≥ 80%）

```kotlin
class <Entity>DomainServiceTest {
    private val repository: <Entity>Repository = mockk()
    private val service = <Entity>DomainService(repository)

    @Test
    fun `get<Entity> should throw when not found`() {
        every { repository.findByIdOrNull(any()) } returns null
        assertThrows<BizException> { service.get<Entity>(<Entity>.<Entity>Id()) }
    }

    @Test
    fun `validate<Field>Uniqueness should throw when duplicate`() {
        every { repository.exists(any()) } returns true
        assertThrows<BizException> { service.validate<Field>Uniqueness("existing") }
    }
}
```

---

## 5.3 CommandHandler 测试（必须，覆盖率 ≥ 80%）

```kotlin
class <Entity>CommandHandlerTest {
    private val repository: <Entity>Repository = mockk(relaxed = true)
    private val domainService: <Entity>DomainService = mockk(relaxed = true)
    private val handler = <Entity>CommandHandler(repository, domainService)

    @Test
    fun `handle Create should create and save entity`() {
        val cmd = <Entity>Cmd.Create(<field> = "test")
        val result = handler.handle(cmd)
        assertNotNull(result.id)
        verify { repository.save(any<<Entity>>()) }
    }
}
```

---

## 5.4 QueryHandler 测试（必须，覆盖率 ≥ 80%）

**测试内容**：handle(GetQuery) 返回 View / null、handle(ListQuery) 返回列表、handle(PageQuery) 分页参数

```kotlin
class <Entity>QueryHandlerTest {
    private val dao: <Entity>Dao = mockk()
    private val handler = <Entity>QueryHandler(dao)

    @Test
    fun `handle GetQuery should return view when found`() {
        val query = <Entity>Query.GetQuery(entityId = 1L)
        val view = <Entity>View(id = 1L)
        every { dao.findById(1L) } returns view

        val result = handler.handle(query)
        assertEquals(view, result)
    }

    @Test
    fun `handle GetQuery should return null when not found`() {
        val query = <Entity>Query.GetQuery(entityId = 999L)
        every { dao.findById(999L) } returns null

        val result = handler.handle(query)
        assertNull(result)
    }

    @Test
    fun `handle ListQuery should delegate to dao`() {
        val query = <Entity>Query.ListQuery(filter = <Entity>Filter(field = "test"))
        val views = listOf(<Entity>View(id = 1L), <Entity>View(id = 2L))
        every { dao.findByXxx("test") } returns views

        val result = handler.handle(query)
        assertEquals(2, result.size)
    }

    @Test
    fun `handle PageQuery should pass page params correctly`() {
        val query = <Entity>Query.PageQuery(filter = <Entity>Filter(), pageNum = 1, pageSize = 10)
        val pageResult = PageResult<<Entity>View>(total = 0, pages = 0, current = 1, size = 10, items = emptyList())
        every { dao.pageByXxx(any(), 1, 10) } returns pageResult

        val result = handler.handle(query)
        assertEquals(0, result.total)
    }
}
```

---

## 5.5 适配器层集成测试（必须，与适配器代码同 PR）

> **定位**：mockk 单元测试覆盖领域逻辑和应用层编排。集成测试覆盖数据库映射、SQL 语法、HTTP 契约。
> **时机**：写完适配器层代码后立即编写，不可延后。同一 PR 内单元测试 + 集成测试必须同时通过。
> **基础设施**：Testcontainers + MySQL 8.0，配置类 `TestcontainersConfiguration`（`@ServiceConnection`），profile `test`。

### 5.5.1 JPA Repository 集成测试

**触发条件**：新增或修改 `JpaRepositories.kt`（含 `@Query` 方法、Specification 查询、Entity 映射变更）

```kotlin
@DataJpaTest
@Import(TestcontainersConfiguration::class)
@ActiveProfiles("test")
class <Entity>JpaRepositoryIT {

    @Autowired
    private lateinit var repository: <Entity>JpaRepository

    @Test
    fun `save and findById should persist and retrieve entity`() {
        val entity = <Entity>.create(<Entity>Attr(<field> = "test"))
        repository.save(entity)
        val found = repository.findById(entity.id!!)
        assertTrue(found.isPresent)
        assertEquals("test", found.get().<field>?.value)
    }

    @Test
    fun `findAll with Specification should filter correctly`() {
        repository.save(<Entity>.create(...))
        val spec = <Entity>Spec.byXxx(<field>)
        val result = repository.findAll(spec, Sort.by(Sort.Direction.ASC, "<field>.value"))
        assertEquals(1, result.size)
    }

    @Test
    fun `custom Query should return expected result`() {
        repository.save(<Entity>.create(...))
        val result = repository.<customMethod>(...)
        assertNotNull(result)
    }

    @Test
    fun `delete should remove entity`() {
        val entity = <Entity>.create(...)
        repository.save(entity)
        repository.delete(entity)
        assertTrue(repository.findById(entity.id!!).isEmpty)
    }
}
```

### 5.5.2 MyBatis Mapper 集成测试

**触发条件**：新增或修改 `Mappers.kt` 或 `XxxMapper.xml`（含 SQL 变更、resultMap 变更）

```kotlin
@MybatisTest
@Import(TestcontainersConfiguration::class)
@ActiveProfiles("test")
class <Entity>MapperIT {

    @Autowired
    private lateinit var jdbcTemplate: JdbcTemplate

    @Autowired
    private lateinit var mapper: <Entity>Mapper

    @BeforeEach
    fun setup() {
        jdbcTemplate.execute("""
            CREATE TABLE IF NOT EXISTS <table> (
                id BIGINT NOT NULL,
                <field> VARCHAR(100) NOT NULL,
                ...
                PRIMARY KEY (id)
            )
        """.trimIndent())
        jdbcTemplate.execute("DELETE FROM <table>")
    }

    @Test
    fun `selectById should return view when record exists`() {
        jdbcTemplate.update("INSERT INTO <table> (...) VALUES (?, ?, ...)", 1L, "test")
        val result = mapper.selectById(1L)
        assertNotNull(result)
        assertEquals("test", result.<field>)
    }

    @Test
    fun `selectById should return null when record not found`() {
        assertNull(mapper.selectById(999L))
    }

    @Test
    fun `selectListByXxx should return matching rows in correct order`() {
        jdbcTemplate.update("INSERT INTO <table> (...) VALUES (?, ?, ...)", 1L, "B")
        jdbcTemplate.update("INSERT INTO <table> (...) VALUES (?, ?, ...)", 2L, "A")
        val result = mapper.selectListByXxx("test")
        assertEquals(2, result.size)
        assertEquals("A", result[0].<field>)  // 验证排序
    }
}
```

### 5.5.3 REST Controller 集成测试

**触发条件**：新增或修改 `Controller.kt`（含路由、请求体、响应结构、错误码变更）

```kotlin
@SpringBootTest
@AutoConfigureMockMvc
@Import(TestcontainersConfiguration::class)
@ActiveProfiles("test")
@DisplayName("<Entity>Controller API")
class <Entity>ControllerIT {

    @Autowired
    private lateinit var mockMvc: MockMvc

    private fun createEntity(name: String = "test"): Long {
        val result = mockMvc.perform(
            post("/api/v1/<entities>")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"<field>":"$name"}""")
        )
            .andExpect(status().isCreated)
            .andReturn()
        return JacksonHelper.mapper.readTree(result.response.contentAsString).get("id").asLong()
    }

    @Nested
    @DisplayName("POST /api/v1/<entities>")
    inner class Create {
        @Test
        fun `should return 201 with correct fields`() {
            mockMvc.perform(
                post("/api/v1/<entities>")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""{"<field>":"test"}""")
            )
                .andExpect(status().isCreated)
                .andExpect(jsonPath("$.<field>", `is`("test")))
        }

        @Test
        fun `should return 400 when required field is blank`() {
            mockMvc.perform(
                post("/api/v1/<entities>")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""{"<field>":""}""")
            )
                .andExpect(status().isBadRequest)
        }

        @Test
        fun `should return 400 when name already exists`() {
            createEntity(name = "duplicate")
            mockMvc.perform(
                post("/api/v1/<entities>")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""{"<field>":"duplicate"}""")
            )
                .andExpect(status().isBadRequest)
        }
    }

    @Nested
    @DisplayName("GET /api/v1/<entities>")
    inner class Query {
        private var entityId: Long = 0

        @BeforeEach
        fun setup() { entityId = createEntity() }

        @Test
        fun `should return entity by id`() {
            mockMvc.perform(get("/api/v1/<entities>/$entityId"))
                .andExpect(status().isOk)
                .andExpect(jsonPath("$.id", `is`(entityId.toInt())))
        }

        @Test
        fun `should return empty body when id not found`() {
            mockMvc.perform(get("/api/v1/<entities>/99999"))
                .andExpect(status().isOk)
                .andExpect { result -> assert(result.response.contentAsString.isEmpty()) }
        }
    }

    @Nested
    @DisplayName("PUT /api/v1/<entities>/{id}")
    inner class Update {
        private var entityId: Long = 0

        @BeforeEach
        fun setup() { entityId = createEntity(name = "old") }

        @Test
        fun `should update and return 200`() {
            mockMvc.perform(
                put("/api/v1/<entities>/$entityId")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""{"<field>":"new"}""")
            )
                .andExpect(status().isOk)
                .andExpect(jsonPath("$.<field>", `is`("new")))
        }

        @Test
        fun `should return 404 when entity not found`() {
            mockMvc.perform(
                put("/api/v1/<entities>/99999")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("""{"<field>":"new"}""")
            )
                .andExpect(status().isNotFound)
        }
    }

    @Nested
    @DisplayName("DELETE /api/v1/<entities>/{id}")
    inner class Delete {
        private var entityId: Long = 0

        @BeforeEach
        fun setup() { entityId = createEntity(name = "to-delete") }

        @Test
        fun `should delete and return 204`() {
            mockMvc.perform(delete("/api/v1/<entities>/$entityId"))
                .andExpect(status().isNoContent)
            mockMvc.perform(get("/api/v1/<entities>/$entityId"))
                .andExpect { result -> assert(result.response.contentAsString.isEmpty()) }
        }

        @Test
        fun `should return 404 when deleting non-existing entity`() {
            mockMvc.perform(delete("/api/v1/<entities>/99999"))
                .andExpect(status().isNotFound)
        }
    }
}
```

### 5.5.4 测试基础设施（已有，无需每次重建）

**Testcontainers 配置类**（Spring Boot `@ServiceConnection` 方式，自动注入 datasource）：

文件：`src/test/kotlin/.../TestcontainersConfiguration.kt`

```kotlin
@TestConfiguration(proxyBeanMethods = false)
class TestcontainersConfiguration {
    @Bean
    @ServiceConnection
    fun mysqlContainer(): MySQLContainer<*> {
        return MySQLContainer(DockerImageName.parse("mysql:8.0"))
    }
}
```

**工作原理**：
- `@ServiceConnection` 是 Spring Boot 原生注解，自动从 Testcontainers 容器读取 `jdbcUrl`、`username`、`password`，注入到 `spring.datasource`
- **`application-test.yaml` 中不配 `spring.datasource.url/username/password`**——这些由 `@ServiceConnection` 在运行时动态提供
- 各 IT 类通过 `@Import(TestcontainersConfiguration::class)` 引入，无需继承基类

**application-test.yaml**（仅配 JPA DDL + MyBatis + 日志）：

文件：`src/test/resources/application-test.yaml`

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: false
  modulith:
    events:
      jdbc:
        schema-initialization:
          enabled: false
mybatis:
  mapper-locations: classpath*:mapper/**/*.xml
logging:
  level:
    com.erke: WARN
    org.testcontainers: INFO
```

### 5.5.5 TDD 与集成测试的关系

| 测试类型 | TDD？ | 时机 | 验证命令 |
|----------|------|------|----------|
| mockk 单元测试 | **是**（先写测试，再写代码） | 写领域/应用层代码之前 | `mvn test` |
| JPA/MyBatis 集成测试 | **否**（需要实体映射/SQL 存在才能跑） | 写完适配器层代码后立即写，同 PR | `mvn verify` |
| REST Controller 集成测试 | **否**（需要全链路联通） | 写完 Controller + CommandHandler 后立即写，同 PR | `mvn verify` |

**核心原则**：集成测试可以后于生产代码写，但**决不延后到下一个 PR**。

### 5.5.6 Spec-测试覆盖检查（apply 完成后强制执行）

> **目的**：确保 spec 中定义的每一个场景都有对应的测试覆盖。

**检查方法**：

1. 读取 `openspec/changes/<change-name>/specs/` 下所有 spec.md 文件
2. 提取 `#### 场景:` 标题下的所有场景
3. 逐条对照已写的测试方法，输出覆盖矩阵：

```
| Spec 场景 | 单元测试 | 集成测试 |
|-----------|---------|---------|
| 新增成功 | ✅ 创建应返回正确的 DTO | ✅ 创建成功应返回201 |
| 名称重复 | ✅ 创建时名称重复应抛出异常 | ✅ 重复应返回400 |
| 名称为空 | ✅ ValueObjectsTest中拒绝空字符串 | ✅ 名称为空应返回400 |
```

4. **如果存在 MISSING**：立即补写缺失的测试，不可标记为"完成"
5. **全部覆盖后**：输出 `Spec 覆盖检查通过：N 个场景全部有测试覆盖`

**覆盖原则**：

- 每个 spec 场景至少有一个测试覆盖（单元测试或集成测试至少其一）
- **写操作场景**：单元测试覆盖领域逻辑 + 集成测试覆盖 HTTP 契约
- **读操作场景**：单元测试覆盖 Handler 逻辑 + 集成测试覆盖 HTTP 契约
- **Bean Validation 场景**：集成测试覆盖（MockMvc + `@Valid`）
- **领域异常场景**：单元测试覆盖（mockk + assertThrows）

**常见遗漏清单**（AI 最容易漏的）：

| 易漏场景 | 原因 | 检查方式 |
|---------|------|---------|
| 编辑时 ID 不存在 | 只测了正常编辑 | 搜索测试名是否含"不存在" |
| 编辑时名称重复 | 只测了创建时重复 | 确认 CommandHandler 有编辑+重复的测试 |
| Bean Validation 边界 | 值对象测试≠HTTP 层验证 | ControllerIT 必须有空值/超长测试 |
| 查询空列表 | 只测了有数据的情况 | QueryHandler + ControllerIT 都需空列表测试 |

---

## 5.6 不需要测试的内容

Events.kt、ErrorCode.kt、Repository.kt（接口）、UseCase.kt（接口）、QueryCase.kt（接口）、Queries.kt、Dao.kt（接口）、Vos.kt、Dtos.kt、Views.kt、Filters.kt

---

## 6. 编码规范速查

| 规范项 | 要求 |
|--------|------|
| 类名后缀 | VO（大写）、DTO（大写）、Cmd、Attr、View、Filter |
| 方法命名 | UseCase/QueryCase 的方法统一用 `handle` |
| 异常抛出 | `BizException.of(ErrorCode, args)`，不直接 `throw RuntimeException` |
| JPA 更新 | 字段更新统一加 `@DynamicUpdate`，避免全字段更新 |
| 分页 | 统一用 `PageHelper.startPage().doSelectPage().toPageResult()` |
| Spec DSL | 唯一性校验统一用 `<Entity>Spec` object + `and()/or()` |
| 事件发布 | 在聚合根领域方法中 `registerEvent()`，不直接用 `ApplicationEventPublisher` |
| 测试命名 | 反引号风格：`` `methodName should expectedBehavior when condition` `` |
| Mock 框架 | MockK（Kotlin），不用 Mockito |
