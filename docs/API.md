# API 文档

## 接口概述

所有接口都以 `/api` 为前缀。

## 知识图谱生成

### 从 URL 生成知识图谱

```
POST /api/generate
```

#### 请求参数

```json
{
    "url": "string",          // 要分析的网页 URL
    "max_nodes": "number",    // [可选] 最大节点数，默认 50
    "depth": "number"         // [可选] 分析深度，默认 1
}
```

#### 响应

```json
{
    "nodes": [
        {
            "id": "string",
            "label": "string",
            "type": "string",
            "url": "string"
        }
    ],
    "edges": [
        {
            "from": "string",
            "to": "string",
            "label": "string"
        }
    ],
    "stats": {
        "node_count": "number",
        "edge_count": "number"
    }
}
```

### 获取图谱分析结果

```
GET /api/analysis/{graph_id}
```

#### 响应

```json
{
    "summary": "string",      // 图谱概要
    "key_entities": [],       // 关键实体列表
    "relationships": []       // 重要关系列表
}
```

## 大模型对话

### 发起对话

```
POST /api/chat
```

#### 请求参数

```json
{
    "message": "string",      // 用户输入
    "graph_id": "string",     // [可选] 相关的图谱 ID
    "context": []             // [可选] 对话上下文
}
```

#### 响应

```json
{
    "response": "string",     // 模型回复
    "references": []          // 引用的知识点
}
```

## 错误响应

所有接口在发生错误时都会返回统一格式的错误信息：

```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
```

### 常见错误代码

- `400`: 请求参数错误
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误
