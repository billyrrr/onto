# 使用 onto

## 申明模型
通过以下方式定义模型：
```python

# DomainModel 表示领域模型，用于储存信息和执行业务
from onto.domain_model import DomainModel
# attrs 用于申明模型中的字段
from onto.attrs import attrs

class Ticket(DomainModel):
    """ 车票对象，用于管理车票的状态 """
    
    # attrs 可以无限叠加参数，例如 attrs.optional.data_key('myStatus') 用于变更字段在数据库中存储的字段名
    status: str = attrs.optional

```

申明模型时应当写出所有的参数

## 申明模型的业务逻辑/方法

```python
from onto.domain_model import DomainModel
from onto.attrs import attrs

class Ticket(DomainModel):
    
    status: str = attrs.optional

    async def mark_as_finished(self):
        """ 用于将 ticket 的状态设置为已完成，可以在方法中修改本地的状态 """
        self.status = 'finished'
```

## 从其它模型远程创建这个模型

```python
from onto.domain_model import DomainModel
from onto.attrs import attrs

class Ticket(DomainModel):
    
    status: str = attrs.optional

    async def mark_as_finished(self):
        """ 用于将 ticket 的状态设置为已完成，可以在方法中修改本地的状态 """
        self.status = 'finished'

        
class VirtualStop(DomainModel):
    """ 虚拟站点对象 """
    
    async def create_ticket(self):
        """
        用户通过虚拟站点创建车票
        """
        
        # 定义一个车票的幂等 id （可以通过 random_id随机生成）
        from onto.utils import random_id
        ticket_id = random_id()
        
        # 初始化一个车票对象
        await Ticket.initializer_proxy(
            doc_id=ticket_id,  # 主键/key（必选）
        ).new(
            doc_id=ticket_id,  # 再填写一次 Key
            status='created',  # 传入 status 的初始值
        )

```

## 从其它模型远程调用这个模型上的函数

```python
from onto.domain_model import DomainModel
from onto.attrs import attrs

class Ticket(DomainModel):
    
    status: str = attrs.optional

    async def mark_as_finished(self):
        """ 用于将 ticket 的状态设置为已完成，可以在方法中修改本地的状态 """
        self.status = 'finished'

        
class VirtualStop(DomainModel):
    """ 虚拟站点对象 """
    
    async def finish_ticket(self, ticket_id: str):
        """
        通过虚拟站点标注车票为已完成（多个环节好写例子）
        """
        
        # 找到 ticket 的“只写”对象
        ticket = Ticket.method_proxy(
            doc_id=ticket_id,
        )

        # 调用 ticket 上的函数
        await ticket.mark_as_finished()

```

## 其它步骤

暂时省略，目前任务需要的 CouponStub 等模型都已创建对应的 "functions.bind"。如果需要定义新的模型，参照以下步骤。

