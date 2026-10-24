**一句话总结**：在 Vue3 项目中，当功能的状态越来越多、布尔变量和嵌套判断难以维护时，可以用 XState 状态机把复杂交互整理成明确的状态转换关系，让每个业务状态都有清晰的边界。

**大纲与主要观点**：

- **一、前言：复杂的交互，难在状态越来越多**
  - 简单按钮点击用 ref 即可，多状态功能（加载、成功、失败、重试、取消）容易变成大量 if/else if
  - 多个布尔值容易出现不合理组合，例如加载中却同时显示成功提示
  - XState 的思路：先定义有哪些状态，再明确每个状态允许的转换

- **二、什么是 XState？**
  - XState 是用于构建状态机和状态图的 JavaScript 库
  - 可把复杂交互整理成明确的状态转换关系，并与 Vue3 组件结合
  - 示例：订单支付流程——待支付 → 支付处理中 → 成功/失败（可重试）
  - 每个状态含义明确，可执行操作集中管理

- **三、安装与基础配置**
  - 安装依赖：`npm install xstate @xstate/vue`
  - 创建 `paymentMachine.js`，用 `createMachine` 定义 idle、processing、success、failed 四个状态及 PAY、SUCCESS、FAILURE、RETRY 转换
  - 状态机本身不负责真实支付请求，需接入后端接口并由接口结果驱动事件

- **四、在 Vue3 组件中使用**
  - 用 `@xstate/vue` 的 `useMachine` 获取 `snapshot` 和 `send`
  - `snapshot.matches()` 判断当前状态，`send()` 发送事件
  - 组件只负责展示界面，状态机负责状态流转
  - 演示用的成功/失败按钮，真实业务中应由支付接口返回结果驱动

- **五、哪些业务适合使用？**
  - 适合：审批流程、设备控制、多步骤表单、弹窗交互，以及设备管理、订单管理和复杂后台系统
  - 不适合：简单开关、选项卡或普通表单，ref、computed 已足够，无需增加复杂度

- **六、总结**
  - Vue3 解决组件响应式和界面更新，XState 管理复杂状态与转换关系
  - 出现大量布尔变量、嵌套判断和难以追踪的流程时，可考虑用状态机重新梳理逻辑
  - 好的状态管理不只是少写几个 if，而是让每种业务状态都有明确边界

尔嵘 尔嵘 *2026年10月22日 00:02*

## 一、前言：复杂的交互，难在状态越来越多

在 Vue3 项目中，简单的按钮点击用 ref 就能解决。但如果一个功能包含加载、成功、失败、重试、取消等多个状态，代码就容易逐渐变成这样：

```go
if (loading.value) {  // ...} else if (error.value) {  // ...} else if (success.value) {  // ...}
```

当状态之间存在相互制约时，仅靠多个布尔值，很容易出现不合理的组合，例如请求还在加载，却同时显示成功提示。

XState 的思路是：先定义系统有哪些状态，再明确每个状态允许执行哪些转换。

![图片](https://mmbiz.qpic.cn/mmbiz_png/Vlia5l9Vc4An53HHwicQHZTeNDywHDSy5fgsm8UnNDR5QFtKoUNiaRRxB3AMbFicRcW2kU1QWNcLJjNTO3icyDKXdhyLCuEug8FwGpe3vy9pEloY/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

## 二、什么是 XState？

XState 是一个用于构建状态机和状态图的 JavaScript 库。它可以把复杂交互整理成明确的状态转换关系，并与 Vue3 组件结合使用。

例如，一个订单支付流程可以定义为：

```bash
<box borderradius="xl"padding={3}gap={2}>   <boxbackground="surface-secondary"radius="lg"padding={3}align="center">     **待支付**   </box>   <rowjustify="center">     <iconname="arrow-down"size="lg" />     <textcolor="secondary"size="sm">点击支付</text>   </row>   <boxbackground="surface"borderradius="lg"padding={3}align="center">     **支付处理中**   </box>   <rowgap={3}align="center">     <boxflex="1"align="center"gap={1}>       <iconname="arrow-down"color="success"size="lg" />       <textsize="sm"color="success">成功</text>     </box>     <boxflex="1"align="center"gap={1}>       <iconname="arrow-down"color="danger"size="lg" />       <textsize="sm"color="danger">失败</text>     </box>   </row>   <rowgap={3}>     <boxflex="1"background="surface-secondary"radius="lg"padding={3}align="center">       **支付完成**     </box>     <boxflex="1"background="surface-secondary"radius="lg"padding={3}align="center">       **可重试**     </box>   </row> </box>
```

每个状态都有明确含义，哪些操作可以执行，也可以集中管理。

## 三、安装与基础配置

在已有的 Vue3 项目中安装依赖：

```nginx
npm install xstate @xstate/vue
```

创建 paymentMachine.js：

```php
import { createMachine } from 'xstate'export const paymentMachine = createMachine({  id: 'payment',  initial: 'idle',  states: {    idle: {      on: {        PAY: 'processing'      }    },    processing: {      on: {        SUCCESS: 'success',        FAILURE: 'failed'      }    },    success: {      type: 'final'    },    failed: {      on: {        RETRY: 'processing'      }    }  }})
```

这段代码定义了四种业务状态，以及支付、成功、失败、重试对应的转换关系。状态机本身不负责真实的支付请求，实际项目还需要接入后端接口，并根据接口结果发送相应事件。

## 四、在 Vue3 组件中使用

创建 PaymentPanel.vue：

```xml
<script setup>import { useMachine } from '@xstate/vue'import { paymentMachine } from './paymentMachine'const [snapshot, send] = useMachine(paymentMachine)</script><template>  <section class="payment-panel">    <h3>订单支付</h3>    <p v-if="snapshot.matches('idle')">      订单等待支付    </p>    <p v-else-if="snapshot.matches('processing')">      正在处理支付……    </p>    <p v-else-if="snapshot.matches('success')">      支付成功    </p>    <p v-else-if="snapshot.matches('failed')">      支付失败，请重试    </p>    <button      v-if="snapshot.matches('idle')"      @click="send({ type: 'PAY' })"    >      开始支付    </button>    <button      v-if="snapshot.matches('processing')"      @click="send({ type: 'SUCCESS' })"    >      模拟支付成功    </button>    <button      v-if="snapshot.matches('processing')"      @click="send({ type: 'FAILURE' })"    >      模拟支付失败    </button>    <button      v-if="snapshot.matches('failed')"      @click="send({ type: 'RETRY' })"    >      重新支付    </button>  </section></template>
```

这里的成功和失败按钮仅用于演示状态转换，真实业务中应由支付接口的返回结果驱动，而不是由用户直接触发。

![图片](https://mmbiz.qpic.cn/mmbiz_png/Vlia5l9Vc4AkZRdXfM0MubSwFZbkBG9nbE2T6uRRaLTicgBjcP9yGg2ib8VgG5lnOzW67waiaKUxqmibiaibI6Dib1Zg2uuicWY5eQYgkRffkryBZx0I/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=1)

snapshot.matches() 用于判断当前状态，send() 用于发送事件。组件只负责展示界面，状态机负责控制状态流转。

## 五、哪些业务适合使用？

审批流程：待提交、审核中、已通过、已驳回。

设备控制：离线、连接中、运行中、故障、恢复中。

多步骤表单：填写资料、校验信息、提交中、完成或失败。

弹窗交互：初始、确认中、执行中、成功、失败。

特别是在设备管理、订单管理和复杂后台系统中，状态机能让业务流程更加直观。

不过，如果只是简单的开关、选项卡或普通表单，Vue3 自带的 ref、computed 已经足够，没有必要为了引入新库而增加复杂度。

## 六、总结

Vue3 解决的是组件响应式和界面更新问题，XState 则帮助我们管理复杂的状态与转换关系。

当一个功能开始出现大量布尔变量、嵌套判断和难以追踪的流程时，可以考虑用状态机重新梳理业务逻辑。

好的状态管理，不只是让代码少写几个 if，而是让每一种业务状态都有明确的边界。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/Vlia5l9Vc4AlGJnTMC0C8uibvYbdG88y31wDdZ65TtJ5RuicV2sLkS2rrNlxlL63VIeLtVmRGQ7wLBlnUoYfnKM18EJJSo1h5dF2jOzNrCaETM/640?wx_fmt=png&from=appmsg&watermark=1#imgIndex=2)

注意：别问我为啥每天都在坚持写Vue3,你一键三连陪你慢慢聊。生活不易，珍惜现在拥有的一切！

孟子曰：“亲亲，仁也；敬长，义也。”孟子说：“亲爱父母亲，便是仁；尊敬兄长便是义。”——（春秋）《孟子·尽心上》。

尔嵘

邀请你前往腾讯公益一起捐

捡回珍珠计划

前端开发 · 目录

作者提示: 个人观点，仅供参考

<iframe src="chrome-extension://kphegobalneikdjnboeiheiklpbbhncm/html/iframePage/dist/index.html"></iframe>