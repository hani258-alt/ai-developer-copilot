# AI 应用开发基础概念笔记（大白话版）



## **FastAPI** 是一个现代、高性能的 **Python Web 框架**，专门用来构建 **API**（应用程序接口）(Application Programming Interface)



## 简单说：它帮你快速搭建一个后端服务，让前端、App、其他程序可以通过 HTTP 请求来调用你的 Python 函数，并拿到数据。

------

## 一句话总结

> **FastAPI = 极快的 Python Web 框架 + 自动生成文档 + 自带数据校验 + 支持异步**

------

## 它解决什么问题？

假设你要写一个接口：用户访问 `https://你的网站/users/1`，返回用户信息。

用原生 Python 会很麻烦（要自己处理 HTTP 解析、路由、JSON 序列化……）。FastAPI 帮你把这些脏活累活干了，你只需要写：

python

```
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "张三"}
```



就这么简单，一个可用的 API 就完成了。

------

## FastAPI 的四大核心优势

| 特点         | 解释                                                         |
| :----------- | :----------------------------------------------------------- |
| **极快**     | 性能可媲美 Node.js 和 Go，是 Python 框架中速度最快的之一     |
| **自动文档** | 访问 `/docs` 就能获得交互式 API 文档（Swagger UI），无需手写 |
| **数据校验** | 利用 Python 类型提示自动校验请求参数、请求体，非法数据自动报错 |
| **支持异步** | 原生支持 `async/await`，轻松处理高并发 I/O 操作（数据库、HTTP 调用） |

------

## 与其它 Python 框架的对比

| 框架        | 特点                            | 适合场景                          |
| :---------- | :------------------------------ | :-------------------------------- |
| **FastAPI** | 现代、快速、异步、自动文档      | 新项目、高性能 API、前后端分离    |
| **Flask**   | 简单灵活、生态丰富              | 小型应用、原型开发、传统 Web 站点 |
| **Django**  | 大而全（自带 ORM、Admin、模板） | 大型复杂网站、内容管理系统        |

------

## 一个完整的 FastAPI 例子

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 内存数据库
fake_db = {1: "新闻一", 2: "新闻二"}

@app.get("/news/{news_id}")
async def get_news(news_id: int):
    if news_id not in fake_db:
        raise HTTPException(status_code=404, detail="新闻不存在")
    return {"id": news_id, "title": fake_db[news_id]}

@app.post("/news/{news_id}")
async def create_news(news_id: int, title: str):
    fake_db[news_id] = title
    return {"message": "创建成功"}
```



- `@app.get` / `@app.post` 定义**路径函数**
- `news_id: int` 自动校验类型
- 自动生成 `/docs` 文档
- 错误自动返回标准 JSON

------

## 为什么叫 “Fast” API？

1. **性能快**：基于 Starlette（ASGI 框架）和 Pydantic（数据校验），性能很高。
2. **开发快**：类型提示 + 自动补全 + 自动文档，写代码飞快。
3. **运行快**：支持异步，能处理大量并发请求。

------

## 你现在已经了解的概念在 FastAPI 中的位置

| 你学过的概念 | 在 FastAPI 中的角色                  |
| :----------- | :----------------------------------- |
| 路径函数     | `@app.get("/path")` 下面的函数       |
| 中间件       | 全局拦截每个请求/响应                |
| 依赖注入     | `Depends()` 提供数据库、认证等       |
| 异步函数     | `async def` 路径函数，不阻塞其他请求 |

------

**总结**：FastAPI 就是让你用最少的代码，快速写出**高性能、自带文档、自动校验**的 API 服务的框架。如果你要做后端接口，它是目前 Python 社区的首选之一。

## 1.FastAPI

### · 是啥：一个能让你写的 Python 代码在网络上“开门迎客”的工具。

### · 比喻：电话亭的“门”和“接线板”。没有它，你写的代码只能在自己电脑里自娱自乐。有了它，别人的电脑才能通过网络找到你的代码，触发它运行。

### · 项目里干嘛：处理来自网页的聊天请求，并把回复送回去。





# 2.API 密钥（API Key）

### · 是啥：一串乱码似的字符，是你的 “大模型电费卡” 或 “AI 服务通行证”。

### · 比喻：你想用 DeepSeek 公司的超级大脑帮你回答问题，不能白嫖（超额度不行）。你得先申请一张卡，把卡号（Key）写在代码里，DeepSeek 才认你。

### · 项目里干嘛：写在 .env 文件里，让代码能合法调用大模型。





# 3.API 调用

## · 是啥：打电话的动作本身。

## · 比喻：你的 Python 代码不需要自己长出 AI 脑子，它只需要拨号给 DeepSeek 公司，把用户的话念一遍，等对方回答。

### · 项目里干嘛：在 /chat 接口里，client.chat.completions.create(...) 这行代码就是拨号动作。





## 4.流式输出（Streaming）

### · 是啥：让 AI 的回复一个字一个字往外蹦，而不是憋半天一股脑全砸过来。

### · 比喻：微信的“对方正在输入…” + 字一个一个弹出来。等快递 vs 看直播拆箱。

### · 项目里干嘛：/chat/stream 接口实现这个，体验更好。





## 5.上下文 / 记忆（Context / Memory）

### · 是啥：让 AI 记得刚才聊过什么。

### · 比喻：你和餐厅服务员刚才所有的对话记录。如果不带记忆，你刚说完“我叫张三”，下一句问“我叫啥？”，AI 会懵。带着记忆问，AI 会翻看记录回答“你叫张三”。

### · 项目里干嘛：代码里维护一个 messages = [] 列表，每次都把历史记录一起发给 DeepSeek。





# 6.JSON

### · 是啥：程序之间通用的“标准快递盒”。

### · 比喻：你和 DeepSeek 打电话不能乱吼，得把“角色”（用户还是 AI）和“内容”（说了啥）按固定格式打包。JSON 就是这个打包格式：{"role": "user", "content": "你好"}。

### · 项目里干嘛：网页传数据给后端用 JSON，后端传数据给 DeepSeek 也用 JSON。





# 7.RESTful API

### · 是啥：一种设计网址和动作的约定。比如大家都约好了：

###   · 用 POST 这个动作表示“提交数据”（发消息）。

###   · 用 /chat 这个网址路径表示“聊天的功能”。

### · 比喻：全国统一的快递单填写规范。收件人写哪、寄件人写哪、物品写哪，大家都按规矩来，快递员才不迷糊。

### · 项目里干嘛：你写 @app.post("/chat") 就是在遵守这个约定。





## 8.Pydantic

### · 是啥：Python 里的一个“数据验货员”。

### · 比喻：快递盒送来，你拆开之前要先检查：里面是不是真的有东西？寄来的不是砖头吧？Pydantic 就是帮你自动检查 JSON 盒子里的东西格式对不对的工具。

### · 项目里干嘛：定义 ChatRequest 和 ChatResponse 类，如果前端发来的 JSON 少字段或类型不对，FastAPI 会直接拒收并报错，不用你写一堆 if 判断。





## 9.SSE（Server-Sent Events）

### · 是啥：流式输出的专用快递通道。

### · 比喻：普通 POST 请求是寄一个包裹，寄完就断联。SSE 是开一条专用流水线，后端可以顺着这条线，把 AI 生成的字一个接一个地推送到前端，推完才关门。

### · 项目里干嘛：/chat/stream 接口返回 StreamingResponse 时，媒体类型写成 text/event-stream，就是告诉浏览器“我要用 SSE 流水线了，你准备好接货”。





## 1.FastAPI与URL

### URL 就是网址，全称是“统一资源定位符”。

### 简单说，你在浏览器地址栏里打的那串东西就是 URL。

### 举个你代码里的例子：

```
http://localhost:8000/book/123
```

### 这个 URL 拆解来看：

### 部分 含义 例子

### http:// 协议（通信规则） http 或 https

### localhost 服务器地址（域名/IP） 本机，相当于 127.0.0.1

### :8000 端口号（哪扇门） FastAPI 默认 8000

### /book/123 路径（要什么资源） 获取 id 为 123 的书

### 对应你的 FastAPI 代码：

```python
@app.get("/book/{id}")    # ← 这个 /book/{id} 就是 URL 的路径部分
async def get_book(id: int):
    return {"普通用户": id}
```

### 当你访问 http://localhost:8000/book/456：

### · /book/456 匹配到 @app.get("/book/{id}")

### · 456 被提取出来传给参数 id

### 通俗理解：

### · URL 就像快递地址：协议=运输方式，域名=城市，端口=门牌号，路径=几楼几室

### · 你的 FastAPI 程序就是快递分拣员，根据 URL 路径决定把请求发给哪个函数处理









# 2.注解

[^注解：用任何Python非原生的东西，都必须先from...import导入]: 

## Python 原生注解（通用）

## 所有参数类型都可以用，只负责标注类型，不做任何处理：

```python
def greet(name: str, age: int) -> str:
    return f"{name} is {age} years old"
```

##  : str、: int 是参数注解

##  -> str 是返回值注解

##  纯 Python 会忽略它们，只作为元数据存在

## FastAPI 特殊注解（增强功能）

## 在 Python 原生注解基础上，FastAPI 提供额外的工具函数来控制参数行为：

```python
from fastapi import Path, Query, Body, Header, Cookie

@app.get("/user/{user_id}")
def get_user(
    user_id: int = Path(..., gt=0),           # 路径参数，大于0
    q: str = Query(None, max_length=50),      # 查询参数，最多50字符
    token: str = Header(...),                 # 请求头，必需...
    session: str = Cookie(None)               # Cookie，可选
):
    pass
```

## 

## 对比表格：

| 类型     | Python原生注解 | FastAPI特殊注解          |
| -------- | -------------- | ------------------------ |
| 路径参数 | id:int         | id: int = Path(...)      |
| 查询参数 | q:str          | q: str = Query(...)      |
| 请求体   | user:User      | user: User = Body(...)   |
| 请求头   | token:str      | token: str = Header(...) |

## 

## 核心区别：

## · Python 原生注解：只是"贴标签"，告诉开发者预期的类型

## · FastAPI 特殊注解：在原生基础上增加验证、默认值、描述、别名等 Web 专用功能

## 你的理解是对的：原生注解是通用的基础，特殊注解是特定场景的增强。 如果不需要特殊功能，直接用原生注解就够了。







# 3.响应类型

---

## 1.默认响应类型（最常用）

FastAPI 默认会自动将返回值转换为 JSON：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 返回字典 → JSON
@app.get("/dict")
def dict_response():
    return {"message": "hello", "code": 200}

# 返回 Pydantic 模型 → JSON
class User(BaseModel):
    name: str
    age: int

@app.get("/user")
def model_response():
    return User(name="张三", age=18)

# 返回列表 → JSON
@app.get("/list")
def list_response():
    return [{"id": 1}, {"id": 2}]
```

结果示例（JSON）：

```json
{"message": "hello", "code": 200}
```

---

## 2.指定响应类型：response_model

### 用 response_model 明确指定返回的数据结构，自动过滤、转换、验证：

```python
from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

class UserIn(BaseModel):
    name: str
    age: int
    password: str   # 密码不打算返回

@app.post("/user", response_model=UserOut)
def create_user(user: UserIn):
    # 返回时自动过滤掉 password，只返回 name, age, email
    return user
```

### 好处：

### · 隐藏敏感字段（如密码）

### · 自动类型转换

### · 生成清晰的 API 文档

---

## 3.不同状态码的响应

```python
from fastapi import status

@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item():
    return {"id": 1, "name": "新商品"}
```

### 常用状态码：

| 状态码 | 常量                  | 含义         |
| ------ | --------------------- | ------------ |
| 200    | HTTP_200_OK           | 默认成功     |
| 201    | HTTP_201_CREATED      | 创建成功     |
| 204    | HTTP_204_NO_CONTENT   | 成功但无内容 |
| 400    | HTTP_400_BAD_REQUEST  | 请求错误     |
| 401    | HTTP_401_UNAUTHORIZED | 未认证       |
| 404    | HTTP_404_NOT_FOUND    | 未找到       |

---

## 4.返回不同类型（非 JSON）

### 返回纯文本

```python
from fastapi.responses import PlainTextResponse

@app.get("/text", response_class=PlainTextResponse)
def text_response():
    return "这是纯文本内容"
```

### 返回 HTML

```python
from fastapi.responses import HTMLResponse

@app.get("/html", response_class=HTMLResponse)
def html_response():
    return "<h1>Hello</h1><p>这是HTML页面</p >"
```

### 返回文件

```python
from fastapi.responses import FileResponse

@app.get("/file")
def file_response():
    return FileResponse("document.pdf", filename="下载的文件.pdf")
```

### 返回重定向

```python
from fastapi.responses import RedirectResponse

@app.get("/old-url")
def redirect():
    return RedirectResponse("/new-url")
```

### 返回 JSON（手动指定）

```python
from fastapi.responses import JSONResponse

@app.get("/custom-json")
def custom_json():
    return JSONResponse(
        content={"data": "something"},
        status_code=200,
        headers={"X-Custom": "value"}
    )
```

---

## 5.响应类型速查表

| 用途     | 响应类            | 示例                             |
| -------- | ----------------- | -------------------------------- |
| 默认JSON | None(不指定)      | return{"key":"value"}            |
| 手动JSON | JSONResponse      | JSONResponse(content={...0})     |
| 纯文本   | PlainTextResponse | return "text"                    |
| HTML     | HTMLResponse      | return "<html>..."               |
| 文件     | FileResponse      | return FileResponse("path")      |
| 重定向   | RedirectResponse  | return RedirectResponse("/url")  |
| 无内容   | Response          | return Response(status_code=204) |

---

## 6.response_model vs 直接返回

| 方式           | 优点                | 缺点                     |
| -------------- | ------------------- | ------------------------ |
| 直接返回字典   | 简单快捷 无自动过滤 | 不生成文档               |
| response_model | 自动过滤，验证      | 文档需要定义Pydantic模型 |

### 推荐： 生产环境用 response_model，开发调试可临时用字典。

---

### 记忆口诀

### 默认返回是 JSON，字典模型都能行

### 敏感字段要过滤，response_model 来指定

### 文本 HTML 和文件，换用 Response 类

### 状态码用常量写，API 文档自动生







# 后端开发中**非常常见**的功能场景

------

## 1. 记录日志

**意思**：把程序运行过程中发生的事记下来，方便以后查问题。

**生活例子**：飞机上的黑匣子，记录飞机所有操作和状态。

**代码例子**：

```python
# 有人访问网站时，记下来
2025-01-15 10:30:22 - 用户 123 访问了 /news
2025-01-15 10:30:25 - 用户 123 查询了新闻 5 号
2025-01-15 10:30:30 - 数据库查询用了 0.5 秒
```

**作用**：出bug时回头看日志，就知道哪里出问题了。



------

## 2. 添加跨域头 (CORS)

**意思**：让你的网站允许别的网站来调用你的接口。

**生活例子**：你家大门本来只让家人进，你给朋友一把钥匙，朋友也能进来了。

**为什么需要**：浏览器安全规则禁止网页A去请求网页B的数据。加了跨域头就等于告诉浏览器"我允许别人来调我"。

**代码例子**：

```python
# 加了这行，任何网站都能调用你的接口
Access-Control-Allow-Origin: *
```



------

## 3. 数据库连接

**意思**：程序连上数据库，才能存或取数据。

**生活例子**：你要从仓库拿货，必须先**打开仓库门**。

**代码例子**：



```python
# 连接数据库
db = connect_to_mysql(host="localhost", user="root", password="123")
# 然后才能查数据
users = db.query("SELECT * FROM users")
```



------

## 4. 用户认证

**意思**：确认你是谁（登录验证）。

**生活例子**：进小区刷门禁卡，刷卡成功才知道你是谁家的。

**代码例子**：

python

```python
def login(username, password):
    if username == "张三" and password == "123456":
        return "登录成功，你是张三"
    else:
        return "用户名或密码错误"
```



------

## 5. 请求限流

**意思**：限制同一个用户短时间内访问太多次，防止恶意攻击。

**生活例子**：游乐园的过山车，每趟只能坐20人，下一趟要等5分钟。你不能连续坐100次。

**代码例子**：



```python
# 同一个用户1分钟内最多访问10次
如果 用户A 在1分钟内请求超过10次:
    返回 "你请求太快了，等会儿再试"
```



------

## 6. 权限检查

**意思**：确认你有资格做某个操作。

**生活例子**：公司大楼，普通员工卡只能进1-5楼，经理卡能进6楼机房。

**代码例子**：



```python
def delete_user(operator, target_user):
    if operator.role != "admin":
        return "你没有权限删除用户，只有管理员可以"
    # 权限通过，执行删除
    delete(target_user)
```



------

## 7. 缓存数据库查询结果

**意思**：把查过的数据存起来，下次再查直接给，不用再查数据库。

**生活例子**：你第一次算1+1=2，记在脑子里。下次再问1+1，直接说2，不用重新算。

**代码例子**：



```python
# 第一次查用户1
user = db.query("SELECT * FROM users WHERE id=1")  # 花了1秒
cache_set("user_1", user)  # 存起来

# 第二次查用户1
user = cache_get("user_1")  # 直接拿到，用了0.01秒，快100倍
```



------

## 一句话总结表

| 术语         | 一句话解释                   |
| :----------- | :--------------------------- |
| 记录日志     | 记下程序干了什么事           |
| 添加跨域头   | 允许别的网站调你的接口       |
| 数据库连接   | 程序连上数据库的门           |
| 用户认证     | 确认你是谁（登录）           |
| 请求限流     | 防止你刷太快                 |
| 权限检查     | 看你有没有资格做某事         |
| 缓存查询结果 | 把查过的数据存起来，下次更快 |

------

## 它们在实际代码中的位置



```python
# 中间件做的事（全局）
记录日志          ← 每个请求都记
添加跨域头        ← 每个响应都加
请求限流          ← 每个请求都检查

# 依赖注入做的事（按需）
数据库连接        ← 需要查数据时才连
用户认证          ← 需要知道是谁时才验证
权限检查          ← 需要确认权限时才检查
缓存查询结果      ← 查完数据后顺手存起来
```





# 

## dotenv 就是把  .env  文件里的配置偷偷塞进系统环境，让你的程序安全、灵活地读取各种设置
