# 代码文档说明

本文档提供Week 2金融数据工程系统的代码文档概览，包括关键概念、设计决策和最佳实践。

## 目录

1. [前复权 vs 后复权](#前复权-vs-后复权)
2. [未来函数防范](#未来函数防范)
3. [数据时间点正确性](#数据时间点正确性)
4. [OHLCV数据一致性](#ohlcv数据一致性)
5. [错误处理策略](#错误处理策略)
6. [性能优化考虑](#性能优化考虑)

---

## 前复权 vs 后复权

### 什么是复权？

复权是调整历史股价以反映分红、送股、配股等公司行为的过程。不复权的价格数据在除权除息日会出现跳空缺口，影响技术分析和回测的准确性。

### 前复权（Forward Adjust）

**定义：** 保持当前价格不变，向前调整历史价格。

**公式：** `调整后价格 = 原始价格 × 复权因子`

**适用场景：**
- ✅ 回测分析
- ✅ 策略开发
- ✅ 技术指标计算

**优点：**
- 避免未来函数：在任何历史时点，只使用该时点之前的信息
- 当前价格真实：最新价格与市场报价一致
- 回测准确：反映真实的交易条件

**示例：**
```python
from src.price_adjuster import PriceAdjuster

# 前复权（回测推荐）
adjuster = PriceAdjuster(client)
adjusted_data = adjuster.forward_adjust(raw_data, '000001.SZ')

# 前复权后，当前价格不变，历史价格被调整
# 假设2024-01-10发生10%分红：
# 原始数据：
#   2024-01-09: close=10.0
#   2024-01-10: close=9.0 (除权)
#   2024-01-11: close=9.1
#
# 前复权后：
#   2024-01-09: close=9.0  (向前调整)
#   2024-01-10: close=9.0
#   2024-01-11: close=9.1  (当前价格不变)
```

### 后复权（Backward Adjust）

**定义：** 保持历史价格不变，向后调整当前价格。

**公式：** `调整后价格 = 原始价格 × (最新复权因子 / 当日复权因子)`

**适用场景：**
- ✅ 价格展示
- ✅ 长期趋势分析
- ✅ 图表可视化

**优点：**
- 价格连续：历史价格曲线平滑，无跳空
- 趋势清晰：长期走势更容易观察

**缺点：**
- ❌ 不适合回测：使用了未来信息（最新的复权因子）
- ❌ 当前价格失真：最新价格与市场报价不一致

**示例：**
```python
# 后复权（展示推荐）
adjusted_data = adjuster.backward_adjust(raw_data, '000001.SZ')

# 后复权后，历史价格不变，当前价格被调整
# 假设2024-01-10发生10%分红：
# 原始数据：
#   2024-01-09: close=10.0
#   2024-01-10: close=9.0 (除权)
#   2024-01-11: close=9.1
#
# 后复权后：
#   2024-01-09: close=10.0 (历史价格不变)
#   2024-01-10: close=9.0
#   2024-01-11: close=9.1 → 10.1 (向后调整)
```

### 选择建议

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 回测策略 | 前复权 | 避免未来函数，确保回测真实性 |
| 技术分析 | 前复权 | 当前价格真实，指标计算准确 |
| 价格展示 | 后复权 | 价格曲线连续，趋势清晰 |
| 长期投资分析 | 后复权 | 更好地展示长期收益 |

**系统默认：** 本系统在回测场景下默认使用前复权，确保时间点正确性。

---

## 未来函数防范

### 什么是未来函数？

未来函数（Look-ahead Bias）是指在历史分析中使用了未来信息的错误。这会导致回测结果过于乐观，实盘交易时无法复现。

### 常见的未来函数陷阱

#### 1. 使用后复权进行回测

```python
# ❌ 错误：后复权使用了未来的复权因子
data = adjuster.backward_adjust(raw_data, '000001.SZ')
# 在2024-01-01回测时，使用了2024-12-31的复权因子

# ✅ 正确：前复权只使用历史信息
data = adjuster.forward_adjust(raw_data, '000001.SZ')
# 在2024-01-01回测时，只使用2024-01-01之前的复权因子
```

#### 2. 使用报告期而非公告日期

```python
# ❌ 错误：使用报告期
# 2023年年报在2024-04-30公布，但报告期是2023-12-31
# 如果在2024-01-01使用这个数据，就是未来函数
financial_data = handler.get_financial_data(
    stock_codes=['000001.SZ'],
    indicators=['pe', 'pb'],
    as_of_date='20240101',  # 查询日期
    date_field='report_date'  # ❌ 使用报告期
)

# ✅ 正确：使用公告日期
financial_data = handler.get_financial_data(
    stock_codes=['000001.SZ'],
    indicators=['pe', 'pb'],
    as_of_date='20240101',  # 查询日期
    date_field='announce_date'  # ✅ 使用公告日期
)
# 只返回公告日期 <= 2024-01-01 的数据
```

#### 3. 数据对齐时使用未来信息

```python
# ❌ 错误：使用未来的行业分类
# 股票在2024-06-01从行业A调整到行业B
# 如果在2024-01-01使用行业B的分类，就是未来函数
industry = mapper.get_stock_industry(
    stock_code='000001.SZ',
    date=None  # ❌ 使用当前分类
)

# ✅ 正确：使用历史时点的分类
industry = mapper.get_stock_industry(
    stock_code='000001.SZ',
    date='20240101'  # ✅ 使用历史日期
)
```

### 系统的未来函数防范机制

#### 1. 前复权默认策略

```python
# src/price_adjuster.py
# 系统默认使用前复权，避免未来函数
DEFAULT_ADJUST_TYPE = 'front'
```

#### 2. 时间点正确性验证

```python
# src/fundamental_handler.py
def get_financial_data(self, stock_codes, indicators, as_of_date):
    """
    获取指定时点的财务数据（时间点正确）
    
    仅返回 announce_date <= as_of_date 的数据
    """
    # 过滤：只使用已公告的数据
    data = data[data['announce_date'] <= as_of_date]
    return data
```

#### 3. 保守日期对齐策略

```python
# src/data_alignment.py
def align_data_sources(price_data, fundamental_data):
    """
    跨数据源对齐，使用保守策略
    
    当存在日期不确定性时，使用较早的日期
    """
    # 使用公告日期而非报告期
    # 使用T-1日的数据而非T日
    pass
```

### 未来函数检查清单

在编写策略时，检查以下几点：

- [ ] 是否使用前复权进行回测？
- [ ] 基本面数据是否使用公告日期？
- [ ] 行业分类是否使用历史时点？
- [ ] 技术指标是否只使用历史数据？
- [ ] 数据对齐是否采用保守策略？

---

## 数据时间点正确性

### 时间点正确性的重要性

在量化交易中，确保在任何历史时点只使用该时点之前的信息至关重要。这是回测准确性的基础。

### 关键时间字段

#### 1. 价格数据

```python
# 日线数据
{
    'date': '20240101',      # 交易日期
    'close': 10.5,           # 收盘价
    # 在T日收盘后，我们知道T日的价格
    # 但只能在T+1日开盘时使用这个信息交易
}
```

#### 2. 基本面数据

```python
# 财务数据
{
    'report_date': '20231231',    # 报告期（财报覆盖的时间段）
    'announce_date': '20240430',  # 公告日期（财报发布的日期）
    'net_profit': 1000000,        # 净利润
    # ⚠️ 关键：只能在announce_date之后使用这个数据
    # 不能在report_date之后就使用
}
```

#### 3. 行业分类数据

```python
# 行业变更
{
    'stock_code': '000001.SZ',
    'effective_date': '20240601',  # 生效日期
    'industry_code': 'SW801010',   # 新行业代码
    # 只能在effective_date之后使用新的行业分类
}
```

### 时间点正确性实现

#### 示例1：基本面数据查询

```python
# src/fundamental_handler.py
def get_financial_data(self, stock_codes, indicators, as_of_date):
    """
    获取指定时点的财务数据
    
    Args:
        as_of_date: 查询时点，格式 'YYYYMMDD'
    
    Returns:
        仅包含 announce_date <= as_of_date 的数据
    """
    # 从数据库获取所有财务数据
    all_data = self._fetch_all_financial_data(stock_codes, indicators)
    
    # 关键：使用公告日期过滤
    # 只返回在as_of_date之前已经公告的数据
    filtered_data = all_data[all_data['announce_date'] <= as_of_date]
    
    # 如果同一报告期有多次公告（更正），使用最新的
    filtered_data = filtered_data.sort_values('announce_date')
    filtered_data = filtered_data.groupby(['stock_code', 'report_date']).last()
    
    return filtered_data
```

#### 示例2：行业分类查询

```python
# src/industry_mapper.py
def get_stock_industry(self, stock_code, date=None):
    """
    获取股票的行业分类
    
    Args:
        stock_code: 股票代码
        date: 查询日期，None表示当前
    
    Returns:
        在指定日期有效的行业分类
    """
    # 获取所有历史行业分类记录
    all_records = self._fetch_industry_history(stock_code)
    
    if date is None:
        # 返回最新的分类
        return all_records.iloc[-1]
    else:
        # 返回在指定日期有效的分类
        # 关键：effective_date <= date
        valid_records = all_records[all_records['effective_date'] <= date]
        
        if valid_records.empty:
            return None
        
        # 返回最接近查询日期的记录
        return valid_records.iloc[-1]
```

#### 示例3：数据对齐

```python
# src/data_alignment.py
def align_data_sources(price_data, fundamental_data):
    """
    对齐价格数据和基本面数据
    
    使用保守策略：当存在不确定性时，使用较早的日期
    """
    result = []
    
    for _, price_row in price_data.iterrows():
        trade_date = price_row['date']
        stock_code = price_row['stock_code']
        
        # 查找在交易日之前已公告的最新财务数据
        # 关键：announce_date <= trade_date
        available_data = fundamental_data[
            (fundamental_data['stock_code'] == stock_code) &
            (fundamental_data['announce_date'] <= trade_date)
        ]
        
        if not available_data.empty:
            # 使用最新的已公告数据
            latest_data = available_data.sort_values('announce_date').iloc[-1]
            
            # 合并数据
            merged_row = {**price_row.to_dict(), **latest_data.to_dict()}
            result.append(merged_row)
    
    return pd.DataFrame(result)
```

### 时间点正确性测试

```python
# tests/property/test_properties_fundamental.py
def test_property_10_point_in_time_correctness():
    """
    属性10：时间点正确性
    
    对于任何查询日期和基本面数据请求，返回的所有数据记录的
    announce_date都应该小于或等于查询日期。
    """
    handler = FundamentalHandler(client)
    
    # 查询2024-01-01的财务数据
    data = handler.get_financial_data(
        stock_codes=['000001.SZ'],
        indicators=['pe', 'pb'],
        as_of_date='20240101'
    )
    
    # 验证：所有记录的公告日期都 <= 查询日期
    assert all(data['announce_date'] <= '20240101')
```

---

## OHLCV数据一致性

### OHLCV数据说明

OHLCV是金融数据的标准格式：

- **O (Open)**: 开盘价 - 交易日第一笔成交价
- **H (High)**: 最高价 - 交易日内最高成交价
- **L (Low)**: 最低价 - 交易日内最低成交价
- **C (Close)**: 收盘价 - 交易日最后一笔成交价
- **V (Volume)**: 成交量 - 交易日总成交股数

### 数据关系约束

正常的OHLCV数据应该满足以下关系：

```python
# 基本关系
high >= open
high >= close
low <= open
low <= close

# 更严格的关系
high >= max(open, close)
low <= min(open, close)

# 成交量
volume >= 0
```

### 复权时的一致性处理

在进行价格复权时，必须同时调整所有价格字段，保持相对关系：

```python
# src/price_adjuster.py
def forward_adjust(self, data, stock_code):
    """前复权处理"""
    # 获取复权因子
    adjust_factors = self.get_adjust_factors(stock_code, start_date, end_date)
    
    # 同时调整所有价格字段
    price_columns = ['open', 'high', 'low', 'close']
    for col in price_columns:
        data[col] = data[col] * data['adjust_factor']
    
    # 成交量通常不调整
    # 因为成交量反映的是实际交易的股数
    
    # 验证调整后的关系仍然成立
    assert all(data['high'] >= data['open'])
    assert all(data['high'] >= data['close'])
    assert all(data['low'] <= data['open'])
    assert all(data['low'] <= data['close'])
    
    return data
```

### 数据质量检查

```python
# src/data_manager.py
def validate_ohlcv_data(self, data):
    """
    验证OHLCV数据质量
    
    检查：
    1. 价格关系是否正确
    2. 是否存在异常值
    3. 是否存在缺失值
    """
    issues = []
    
    # 检查价格关系
    invalid_high = data[data['high'] < data['open']] | data[data['high'] < data['close']]
    if len(invalid_high) > 0:
        issues.append(f"发现 {len(invalid_high)} 条记录的最高价异常")
    
    invalid_low = data[data['low'] > data['open']] | data[data['low'] > data['close']]
    if len(invalid_low) > 0:
        issues.append(f"发现 {len(invalid_low)} 条记录的最低价异常")
    
    # 检查负价格
    negative_prices = data[
        (data['open'] < 0) | (data['high'] < 0) |
        (data['low'] < 0) | (data['close'] < 0)
    ]
    if len(negative_prices) > 0:
        issues.append(f"发现 {len(negative_prices)} 条记录存在负价格")
    
    # 检查异常成交量
    if (data['volume'] < 0).any():
        issues.append("发现负成交量")
    
    # 检查缺失值
    missing = data[['open', 'high', 'low', 'close', 'volume']].isnull().sum()
    if missing.any():
        issues.append(f"发现缺失值: {missing.to_dict()}")
    
    return issues
```

---

## 错误处理策略

### 错误分类

系统定义了以下错误类别：

```python
# config.py
class XtDataError(Exception):
    """XtData系统基础异常"""
    pass

class ConnectionError(XtDataError):
    """API连接相关错误"""
    pass

class DataError(XtDataError):
    """数据相关错误"""
    pass

class ValidationError(XtDataError):
    """数据验证错误"""
    pass

class StorageError(XtDataError):
    """存储相关错误"""
    pass
```

### 错误处理原则

#### 1. 快速失败（Fail Fast）

在函数入口处进行参数验证，无效输入立即返回错误：

```python
def download_history_data(self, stock_codes, start_date, end_date):
    """下载历史数据"""
    # 快速失败：立即验证参数
    self._validate_stock_codes(stock_codes)
    self._validate_date_range(start_date, end_date)
    
    # 参数有效后才继续执行
    # ...
```

#### 2. 详细错误消息

错误消息应该包含足够的上下文信息，帮助用户快速定位问题：

```python
# ❌ 不好的错误消息
raise ValueError("Invalid input")

# ✅ 好的错误消息
raise ValueError(
    f"无效的股票代码格式: {stock_code}。"
    f"正确格式: '000001.SZ' 或 '600000.SH'"
)
```

#### 3. 优雅降级（Graceful Degradation）

部分数据失败不应该影响整个流程：

```python
def download_history_data(self, stock_codes, start_date, end_date):
    """下载历史数据"""
    all_data = []
    
    for stock_code in stock_codes:
        try:
            data = self._fetch_history_data(stock_code, start_date, end_date)
            all_data.append(data)
        except Exception as e:
            # 记录错误但继续处理其他股票
            logger.error(f"获取股票 {stock_code} 数据失败: {str(e)}")
            continue
    
    # 返回成功获取的数据
    return pd.concat(all_data) if all_data else pd.DataFrame()
```

#### 4. 日志记录

所有错误都应该记录到日志文件：

```python
try:
    data = self._fetch_data(stock_code)
except Exception as e:
    # 记录详细的错误信息
    logger.error(
        f"获取数据失败: stock_code={stock_code}, "
        f"error={str(e)}, "
        f"traceback={traceback.format_exc()}"
    )
    raise
```

### 错误处理示例

#### 示例1：连接错误处理

```python
# src/xtdata_client.py
def connect(self):
    """连接到XtData服务"""
    for attempt in range(self.retry_times):
        try:
            # 尝试连接
            self._establish_connection()
            return True
        except ConnectionError as e:
            logger.warning(f"连接失败 (尝试 {attempt + 1}/{self.retry_times}): {str(e)}")
            
            if attempt < self.retry_times - 1:
                # 还有重试机会，等待后重试
                time.sleep(self.retry_delay)
            else:
                # 重试次数用尽，抛出异常
                error_msg = f"连接失败，已重试 {self.retry_times} 次"
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e
    
    return False
```

#### 示例2：数据验证错误

```python
# src/data_retriever.py
def _validate_stock_codes(self, stock_codes):
    """验证股票代码"""
    if not stock_codes:
        raise ValidationError("股票代码列表不能为空")
    
    for code in stock_codes:
        if '.' not in code:
            raise ValidationError(
                f"无效的股票代码格式: {code}。"
                f"正确格式: '000001.SZ' 或 '600000.SH'"
            )
```

#### 示例3：存储错误处理

```python
# src/data_manager.py
def save_market_data(self, data, data_type, stock_code):
    """保存市场数据"""
    try:
        # 尝试保存到HDF5
        with pd.HDFStore(self.hdf5_path, mode='a') as store:
            key = f"/{data_type}/{stock_code}"
            store.put(key, data, format='table')
        
        logger.info(f"数据保存成功: {stock_code}, {len(data)} 条记录")
    
    except Exception as e:
        error_msg = f"保存数据失败: {stock_code}, {str(e)}"
        logger.error(error_msg)
        raise StorageError(error_msg) from e
```

---

## 性能优化考虑

### 1. 批量处理

避免逐个处理，使用批量操作：

```python
# ❌ 低效：逐个处理
for stock_code in stock_codes:
    data = retriever.download_history_data([stock_code], start_date, end_date)
    manager.save_market_data(data, 'daily', stock_code)

# ✅ 高效：批量处理
data = retriever.download_history_data(stock_codes, start_date, end_date)
manager.save_market_data(data, 'daily')
```

### 2. 缓存机制

对于不经常变化的数据，使用缓存：

```python
# src/industry_mapper.py
class IndustryMapper:
    def __init__(self, client):
        self.client = client
        self._industry_cache = {}  # 缓存行业结构
    
    def get_industry_structure(self):
        """获取行业结构（带缓存）"""
        if 'structure' in self._industry_cache:
            return self._industry_cache['structure']
        
        # 从API获取
        structure = self._fetch_industry_structure()
        
        # 缓存结果
        self._industry_cache['structure'] = structure
        
        return structure
```

### 3. 增量更新

避免重复下载已有数据：

```python
# src/data_manager.py
def incremental_update(self, retriever, stock_codes, data_type='daily'):
    """增量更新"""
    new_records = 0
    
    for stock_code in stock_codes:
        # 获取最后更新日期
        last_date = self.get_last_update_date(data_type, stock_code)
        
        if last_date:
            # 只下载新数据
            start_date = self._next_trading_day(last_date)
        else:
            # 首次下载，获取全部历史数据
            start_date = '20200101'
        
        end_date = datetime.now().strftime('%Y%m%d')
        
        # 下载新数据
        new_data = retriever.download_history_data(
            [stock_code],
            start_date,
            end_date
        )
        
        if not new_data.empty:
            # 保存新数据
            self.save_market_data(new_data, data_type, stock_code)
            new_records += len(new_data)
    
    return new_records
```

### 4. HDF5优化

使用HDF5的高级特性提升性能：

```python
# 使用压缩
store.put(key, data, format='table', complib='blosc', complevel=9)

# 使用索引
store.create_table_index(key, columns=['date'], optlevel=9)

# 使用查询而非加载全部数据
data = store.select(
    key,
    where='date >= "20240101" & date <= "20240110"'
)
```

### 5. 速率限制

避免触发API速率限制：

```python
# src/data_retriever.py
def download_history_data(self, stock_codes, start_date, end_date):
    """下载历史数据"""
    all_data = []
    
    # 批量处理
    for i in range(0, len(stock_codes), self.batch_size):
        batch_codes = stock_codes[i:i + self.batch_size]
        
        # 处理批次
        batch_data = self._fetch_batch(batch_codes, start_date, end_date)
        all_data.append(batch_data)
        
        # 速率限制：批次间延迟
        if i + self.batch_size < len(stock_codes):
            time.sleep(self.rate_limit_delay)
    
    return pd.concat(all_data)
```

---

## 总结

本文档涵盖了Week 2金融数据工程系统的核心概念和最佳实践：

1. **前复权 vs 后复权**：理解两种复权方法的区别和适用场景
2. **未来函数防范**：确保回测的时间点正确性
3. **数据时间点正确性**：正确处理不同数据源的时间字段
4. **OHLCV数据一致性**：保持价格数据的内在关系
5. **错误处理策略**：构建健壮的错误处理机制
6. **性能优化考虑**：提升系统性能和效率

这些概念和实践是构建可靠量化交易系统的基础。在开发策略时，请始终牢记这些原则。

---

**相关文档：**
- [README.md](../README.md) - 项目概览和快速开始
- [示例脚本](../examples/README.md) - 实践示例
- [XtData API文档](xtdata.md) - API参考
