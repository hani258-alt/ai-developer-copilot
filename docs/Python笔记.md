# Python笔记

```python
#1.变量与数据类型
#Python是动态类型语言，变量不需要声明类型，解释器会自动推断 “ ”自动判断为字符串变量，
name="张三"
age=20
height=1.75
is_student=True



#f-string格式化输出：在字符串前加f,用{变量名}直接嵌入变量
print(f"我叫{name}，今年{age}岁，身高{height}米，学生身份{is_student}")



#2.常用数据结构
#列表list:可变，有序，用[]
fruits=["苹果"."香蕉","橙子"]
fruits.append("葡萄")#尾部添加
fruits.remove("香蕉")#按值删除
print(f"列表内容：{fruits},第一个水果是：{fruits[0]}")#索引从0开始



#元组tuple:不可变，有序，用（）
#适合存储不希望被修改的数据，比如坐标，配置项
point=(10,20)
print(f"坐标：x={point[0]},y={point[1]}")



#字典dict:键值对，用{}，是处理JSON数据的核心
#{键:值}必须成对出现，对与对之间用英文逗号隔开
student={
    "name":"李四"，
    "age":21,
    "skills":["Python","Flask","MySQL"]
}
print(f"学生姓名：{student['name']},掌握的技能：{student['skills']}")




#集合set:无序，不重复，用{}或set(),常用于去重
numbers=[1,2,3,4,4,5]
unique_numbers=set(numbers)
print(f"去重后的数字：{unique_numbers}")




#3.流程控制
#if-elif-else条件判断
score=85
if score>=90:
    grade="A"
elif score>=80:
    grade="B"
else:
    grade="C"
print(f"分数{score}的等级是:{grade}")

#for循环：遍历序列或可迭代对象
for i in range(3):#range(3)生成0，1，2
    print(f"第{i+1}次循环")
    
for fruit in fruits:
    printf(f"我喜欢吃{fruit}")
    
#while循环：条件满足时一直执行
count=0
while count<3:
	print(f"计数{count}")
    count+=1
    
    
    
    
    
    
#4.函数：代码复用的基础
#def关键字定义函数，参数可以有默认值
def greet(name,greeting="你好"):
#这是一个文档字符串（docstring）,用于描述函数功能
#调用时如果不传greeting,默认使用你好.

	return f"{greeting},{name}!"

#调用函数
message=greet("王五")
print(message)#王五，你好
message2=greet("赵六"，"晚上好")
print(message2)#赵六，晚上好






#5.类与面向对象（项目工程化）（先有类再有对象）
class Dog:
    #初始化方法（构造函数），创建对象时自动调用
    def _init_(self,name,age):
        self.name=name
        self.age=age
        
        #实例方法
        def bark(self):
            print(f"{self.name}在汪汪叫！")

           
#创建对象（实例化）
my_dog=Dog("旺财",3)
my_dog.bark()
print(f"{}")

```

# 注意事项：

## 1.输出

```python
id=123

#不加f
return {"普通用户":"用户ID是{id}"}#结果：{"普通用户":"用户ID是{id}"}

#加f
return {"普通用户":f"用户ID是{id}"}#结果：{"普通用户":"用户ID是123"}
```

- f代表format(格式化)
- {变量名}是一个占位符，会被变量的值替换
- 没有f,Python就把{name}当成普通字符{name}本身





# 一，异步函数

## 1.定义：

## 	是使用  async def  定义的函数，它允许程序在等待某件事（如读文件、查数据库、发网络请求）完成时，先去做其他事情，而不是傻等着。

## 2.代码对比：

```python
# 同步函数 - 会卡住
def get_data():
    time.sleep(3)  # 睡3秒，什么事都做不了
    return "完成"

# 异步函数 - 不卡住
async def get_data():
    await asyncio.sleep(3)  # 主动让出控制权，让别人先跑
    return "完成"
```

## 3.关键点:

- ###  await ：只能用在异步函数内部，表示“先去忙别的，等这个结果回来再继续” 

- ###  不自动异步：写了  async  但里面全是普通代码，依然是同步执行 

- ### 需要事件循环：异步函数需要  asyncio.run()  或 FastAPI/Uvicorn 提供的环境来运行  

  

  

  ## 4.为什么 FastAPI 用异步？ 

  ```python
  @app.get("/news/{id}")
  async def get_news(id: int):      # 异步函数
      data = await db.fetch(id)      # 等待数据库时，可以处理其他请求
      return data
  ```

  ### 当有1000个用户同时访问时，异步方式不会因为某个请求在等数据库而阻塞其他请求，大大提升并发能力。 

  ### 简单说：同步 = 一心一意，异步 = 一心多用(高效)







# 二，路径函数：

## 1.定义：路径函数就是 FastAPI 中用装饰器声明的函数，负责处理特定 URL 的请求并返回响应。



## 2.拆解术语

| 词   | 含义                             |
| ---- | -------------------------------- |
| 路径 | URL 地址，如  /user 、 /news/123 |
| 函数 | Python 的  def  或  async def    |

## 例子

```python
@app.get("/")           # 路径 = "/"
def root():             # 这就是路径函数
    return {"message": "Hello"}

@app.get("/user/{id}")  # 路径 = "/user/123"
async def get_user(id: int):  # 这也是路径函数
    return {"id": id}

@app.post("/news")      # 路径 = "/news"
def create_news():      # 这也是路径函数
    return {"status": "ok"}
```

## 核心特征

### 1.装饰器指定路径和方法**：`@app.get()`、`@app.post()`、`@app.put()` 等

### 2.**函数名随便起**（但要见名知义）

### 3.**返回值就是 HTTP 响应**（会自动转成 JSON）



## 为什么叫“路径函数”？

### 因为 FastAPI 源码和官方文档就这么叫 —— 它把 HTTP 方法（GET、POST 等）+ URL 路径（/user、/news）组合起来定义的路由，对应的处理函数就叫 **路径函数**（Path Function）。

### 你也可以理解为：**“路径函数 = 视图函数 = 路由处理函数”**，只是 FastAPI 的术语。













# 三，中间件与依赖注入

| 维度         | 中间件 (Middleware)               | 依赖注入 (Dependency Injection) |
| :----------- | :-------------------------------- | :------------------------------ |
| **核心作用** | 拦截 HTTP 请求/响应，做全局预处理 | 为路径函数提供所需的值/服务     |
| **处理阶段** | 请求进入 → 路径函数前             | 路径函数执行前                  |
| **作用范围** | 全局（所有请求）                  | 按需（只注入到指定路径函数）    |

------

## 具体区别

### 中间件

```python
@app.middleware("http")
async def log_request(request, call_next):
    print("1. 请求进来了")      # 请求前
    response = await call_next(request)  # 执行路径函数
    print("2. 响应要出去了")    # 响应后
    return response
```



- 像一个**安检门**，每个请求都要经过
- 可以修改请求/响应对象
- 不知道具体路径函数需要什么

### 依赖注入

```python
def get_db():
    return Database()

@app.get("/user")
async def get_user(db = Depends(get_db)):  # 只注入到这个函数
    return db.query()
```



- 像一个**外卖员**，只有你需要时才送东西过来
- 只提供给声明的路径函数
- 可以复用复杂逻辑（数据库、认证、权限检查）

------

## 优点对比

| 中间件的优点                       | 依赖注入的优点                 |
| :--------------------------------- | :----------------------------- |
| ✅ 全局统一处理（日志、CORS、限流） | ✅ 代码复用，减少重复           |
| ✅ 不侵入业务代码                   | ✅ 依赖关系清晰可见             |
| ✅ 适合处理协议层面的问题           | ✅ 便于单元测试（轻松 Mock）    |
| ✅ 可修改响应头/状态码              | ✅ 支持作用域（请求级、会话级） |
| ✅ 性能影响小（只做一次）           | ✅ 可嵌套组合多个依赖           |

------

## 实际使用场景

| 场景                  | 用中间件                                 | 用依赖注入 |
| :-------------------- | :--------------------------------------- | :--------- |
| 记录所有请求日志      | ✅                                        | ❌          |
| 添加 CORS 跨域头      | ✅                                        | ❌          |
| 数据库连接            | ❌                                        | ✅          |
| 用户认证/获取当前用户 | ❌（全局认证用中间件，获取用户信息用 DI） | ✅          |
| 请求限流（IP 级别）   | ✅                                        | ❌          |
| 权限检查（特定接口）  | ❌                                        | ✅          |
| 缓存数据库查询结果    | ❌                                        | ✅          |

------

## 总结

- **中间件**：横向通用能力，所有请求必经之路
- **依赖注入**：纵向特定能力，只为需要的函数提供

两者不是互斥的，经常配合使用：

```python
# 中间件做全局日志
# 依赖注入提供数据库连接和当前用户
@app.get("/profile")
async def profile(db=Depends(get_db), user=Depends(get_current_user)):
    return db.get_user(user.id)
```









# 四，分页参数

**分页参数**是 API 请求中用来**控制每次返回多少条数据**的参数，避免一次返回成千上万条数据把系统拖垮。

## 为什么需要分页？

假设你的数据库有 10 万条新闻。如果一次性全部返回：

- 传输要很久（几十 MB 甚至 GB）
- 前端渲染会卡死
- 数据库查询极慢

分页就像**看书不一次全读**，一页只看 20 行。

------

## 常见的分页参数

| 参数名                | 含义           | 例子                         |
| :-------------------- | :------------- | :--------------------------- |
| `page`                | 第几页         | `page=1` 表示第一页          |
| `page_size` / `limit` | 每页多少条     | `limit=10` 表示一页 10 条    |
| `offset`              | 跳过多少条     | `offset=20` 表示跳过前 20 条 |
| `cursor`              | 游标（更高级） | `cursor=1630000000` 时间戳   |

------

## 最简单常用的形式：`page` + `size`

请求：`GET /news?page=2&size=10`

- `page=2`：要第二页
- `size=10`：每页 10 条

后端计算：跳过 `(page-1)*size = 10` 条，取 10 条。

------

## FastAPI 代码示例

```python
from fastapi import FastAPI, Query

app = FastAPI()

fake_db = [{"id": i, "title": f"新闻{i}"} for i in range(1, 1001)]  # 1000条数据

@app.get("/news")
def get_news(
    page: int = Query(1, ge=1),      # 默认第1页，最小1
    size: int = Query(10, ge=1, le=100)  # 默认每页10条，最多100条
):
    start = (page - 1) * size
    end = start + size
    return {
        "page": page,
        "size": size,
        "total": len(fake_db),
        "items": fake_db[start:end]
    }
```



访问 `/news?page=2&size=5` 会返回第 6~10 条新闻。

------

## 另一种风格：`limit` + `offset`

python

```
@app.get("/news")
def get_news(limit: int = 10, offset: int = 0):
    return fake_db[offset:offset+limit]
```



请求 `/news?limit=20&offset=40` 返回第 41~60 条。

------

## 前端配合

分页参数通常配合**总条数**一起返回，前端就能渲染页码：

```json
{
  "page": 2,
  "size": 10,
  "total": 1000,
  "pages": 100,
  "items": [...]
}
```



------

## 一句话总结

> **分页参数 = 告诉后端“我要第几页，每页多少条”，避免一次返回太多数据。**





# 五，ORM

**ORM** 的全称是 **Object-Relational Mapping**，中文叫**对象关系映射**。你可以把它理解成一个“翻译官”，在**编程语言中的对象**和**关系型数据库中的表**之间自动做映射和转换，让你可以用操作对象的方式来操作数据库，而不用手写 SQL。

------

### 一句话理解

有了 ORM，数据库里的一张表就是一个**类**，表里的一行就是一个**对象**，字段就是对象的**属性**。你只要操作这个对象并调用保存方法，ORM 就会帮你生成对应的 SQL 并执行。

比如，你要插入一个用户：

```python
# 不用写 INSERT INTO users (name, age) VALUES ('张三', 25)
user = User(name='张三', age=25)
user.save()
```



------

### 为什么需要 ORM？

面向对象的编程模型和关系数据库的模型天然存在差异，这被称为**“阻抗不匹配”**：

- 代码里是 **类、对象、继承、多态**
- 数据库里是 **表、行、列、外键、SQL**

ORM 就是为了弥补这个差异，让开发者专注业务逻辑，而不是拼写 SQL 字符串。

------

### ORM 的工作原理（简化版）

1. **映射定义**
   你用类定义数据结构，并通过注解/配置把类的属性映射到表的字段上。

   ```python
   class User(BaseModel):
       __tablename__ = 'users'
       id = Column(Integer, primary_key=True)
       name = Column(String)
       age = Column(Integer)
   ```

   

2. **操作对象**
   执行增删查改时，你使用的是对象和方法：

   python

   ```
   users = session.query(User).filter(User.age > 18).all()  # 查询
   user.name = '李四'                                       # 更新
   session.delete(user)                                     # 删除
   ```

   

3. **自动生成 SQL**
   ORM 引擎在底层把这些操作翻译成 SQL，发往数据库，再把返回的结果自动转换成对象。

------

### ORM 的优点

- **开发效率高**：不需要写大量的重复性 SQL，业务代码更短。
- **代码可读性强**：直接操作对象，更贴近业务思维。
- **数据库可移植性好**：因为屏蔽了不同数据库的方言，切换 MySQL/PostgreSQL 等成本很低。
- **安全性更高**：内置使用参数化查询，可以有效防止 SQL 注入。
- **附带有用工具**：如自动建表、数据迁移、关联懒加载等。

------

### ORM 的缺点 / 需要注意的地方

- **性能不如手工优化过的 SQL**：自动生成的 SQL 可能查询了多余的字段，或出现 N+1 查询问题。
- **复杂查询能力有限**：多表联查、子查询、窗口函数等非常复杂的 SQL，用 ORM 写来往往很绕，有时还不如直接写原生 SQL。
- **学习成本**：虽然简化了 SQL，但仍需学习 ORM 框架本身的概念和用法，且不理解底层 SQL 可能导致性能陷阱。
- **抽象泄露**：最终还是要理解数据库的锁、事务、索引等，调试时也得看生成的 SQL。

------

### 主流编程语言中的常见 ORM

| 语言                    | 常见 ORM / 数据库工具                             |
| :---------------------- | :------------------------------------------------ |
| Java                    | Hibernate, MyBatis（半 ORM）, JPA                 |
| Python                  | Django ORM, SQLAlchemy, Peewee                    |
| PHP                     | Eloquent (Laravel), Doctrine                      |
| C# (.NET)               | Entity Framework Core, Dapper（半自动）           |
| JavaScript / TypeScript | TypeORM, Prisma, Sequelize, Knex.js（查询构建器） |
| Go                      | GORM, Ent                                         |

> 像 MyBatis 或 Dapper 通常被称为“半 ORM”，因为它们并不自动生成完整的 SQL，而是让你手写 SQL，但帮你做结果集到对象的映射。

------

### 什么时候该用 ORM？

- **适用场景**：大多数日常的系统功能，如用户管理、内容发布、电商订单等，ORM 可以极大提升效率。
- **需谨慎的场景**：极高的性能要求、特别复杂的统计分析查询，可以选择 ORM 来做基础 CRUD，复杂查询用原生 SQL 或者单独的查询构建器。

------

简单说：**ORM 让你用面向对象的方式玩转数据库，把繁琐的 SQL 藏在了身后。** 它是一个在开发效率和运行性能之间的权衡工具，现代项目几乎都会用到它。



# 六，装饰器

# Python装饰器详解：概念、原理与应用场景

## 1. 什么是装饰器？

Python装饰器是一种特殊类型的函数，它能够**在不修改原函数代码的情况下**，为函数或方法添加新的功能。装饰器本质上是一个**高阶函数**——即接受函数作为参数并返回一个新函数的函数。

### 基本语法示例

```Python
def my_decorator(func):
    def wrapper():
        print("函数调用前执行的操作")
        func()
        print("函数调用后执行的操作")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

当调用`say_hello()`时，实际上执行的是被`wrapper`函数包装后的增强版本。

## 2. 装饰器的核心原理

装饰器基于Python的**一等函数特性**（函数可以作为参数传递和返回）实现。使用`@`符号只是语法糖，等价于：

```Python
say_hello = my_decorator(say_hello)
```

**执行顺序**：当多个装饰器应用于同一函数时，它们按照**从内到外**的顺序执行。

## 3. 装饰器的应用场景

### 3.1 日志记录

自动记录函数的调用信息，包括函数名、参数和返回值。

```Python
def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"调用函数 {func.__name__}，参数: {args} {kwargs}")
        result = func(*args, **kwargs)
        print(f"函数 {func.__name__} 返回: {result}")
        return result
    return wrapper
```

### 3.2 性能监控/计时

测量函数执行时间，用于性能分析和优化。

```Python
import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行时间: {end_time-start_time:.4f}秒")
        return result
    return wrapper
```

### 3.3 权限验证

在Web开发中检查用户权限，保护敏感操作。

```Python
def requires_admin(func):
    def wrapper(*args, **kwargs):
        if not kwargs.get('is_admin'):
            raise PermissionError("需要管理员权限")
        return func(*args, **kwargs)
    return wrapper
```

### 3.4 缓存结果

使用缓存避免重复计算，提高程序性能。

```Python
from functools import lru_cache

@lru_cache(maxsize=32)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 3.5 输入验证

验证函数参数的合法性。

```Python
def validate_positive(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError("参数必须为正数")
        return func(*args, **kwargs)
    return wrapper
```

## 4. 高级装饰器用法

### 4.1 带参数的装饰器

装饰器本身也可以接受参数，增加灵活性。

```Python
def repeat(num_times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")
```

### 4.2 类装饰器

使用类来实现装饰器功能。

```Python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.num_calls = 0
    
    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        print(f"调用次数: {self.num_calls}")
        return self.func(*args, **kwargs)

@CountCalls
def example():
    print("函数执行")
```

### 4.3 保留元数据

使用`functools.wraps`保留原函数的元信息。

```Python
from functools import wraps

def my_decorator(func):
    @wraps(func
```
