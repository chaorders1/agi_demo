# Watermark API 使用指南

本文档介绍如何使用FastAPI实现的水印REST API，以及如何在NextJS前端中调用这些API。

## 🔗 快速连接信息

- **API服务器地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs` (实时交互测试)
- **API状态**: ✅ 服务器已启动并运行
- **跨域支持**: ✅ 已配置支持NextJS默认端口(3000)

## 🚀 启动API服务器

```bash
# 安装依赖
pip install -r requirements.txt

# 启动API服务器
python run_api.py
```

服务器启动后，访问以下URL：
- **API文档**: http://localhost:8000/docs (Swagger UI)
- **根端点**: http://localhost:8000/
- **健康检查**: http://localhost:8000/api/health

## 📡 API端点

### 1. 添加水印 - POST /api/watermark/add

向图片添加不可见水印。

**请求参数**:
- `image`: 图片文件 (multipart/form-data)
- `text`: 水印文本 (form field)
- `method`: 水印算法，可选 "dwtDct" 或 "rivaGan" (form field, 默认dwtDct)

**响应**:
```json
{
  "success": true,
  "message": "水印添加成功",
  "output_filename": "uuid_image_watermarked.png",
  "download_url": "/api/download/uuid_image_watermarked.png"
}
```

### 2. 检测水印 - POST /api/watermark/detect

检测图片中是否包含指定的水印内容。🧠 **支持智能长度推断！**

**请求参数**:
- `image`: 图片文件 (multipart/form-data)
- `watermark`: 期望的水印内容 (form field)
- `method`: 水印算法 (form field, 默认dwtDct)
- `length`: 水印长度(位) (form field, **留空推荐**，会智能推断并尝试多种长度)

**智能特性**:
- 🎯 **自动长度推断**: 根据水印文本自动计算最佳长度
- 🔄 **多长度尝试**: 自动尝试多种可能的长度组合
- 📊 **置信度优选**: 返回置信度最高的检测结果

**响应**:
```json
{
  "success": true,
  "has_watermark": true,
  "confidence": 0.95,
  "decoded_content": "SocialNetwork0",
  "message": "检测完成 (使用长度: 96 位)"
}
```

### 3. 提取水印 - POST /api/watermark/extract

从图片中提取指定长度的水印内容。

**请求参数**:
- `image`: 图片文件 (multipart/form-data)
- `length`: 水印长度(位) (form field, **留空使用96位**，建议先用scan扫描)
- `method`: 水印算法 (form field, 默认dwtDct)

**响应**:
```json
{
  "success": true,
  "watermark_content": "SocialNetwork0",
  "message": "水印提取成功 (使用长度: 96 位)"
}
```

### 4. 扫描水印 - POST /api/watermark/scan

扫描图片中可能存在的任何水印内容。

**请求参数**:
- `image`: 图片文件 (multipart/form-data)
- `method`: 水印算法 (form field, 默认dwtDct)
- `max_length`: 最大尝试长度(位) (form field, 默认512)
- `verbose`: 是否包含原始字节数据 (form field, 默认false)

**响应**:
```json
{
  "success": true,
  "found_watermarks": [
    {
      "length": 96,
      "content": "SocialNetwork0",
      "raw_bytes": "536f6369616c4e6574776f726b30"
    }
  ],
  "message": "扫描完成，发现 1 个可能的水印"
}
```

### 5. 长度推荐 - POST /api/watermark/suggest-length

根据水印文本推荐最佳的长度设置。🧠 **智能长度计算**

**请求参数**:
- `text`: 水印文本 (form field)

**响应**:
```json
{
  "success": true,
  "text": "SocialNetwork0",
  "text_byte_length": 14,
  "recommended_length": 96,
  "suggested_lengths": [32, 64, 96, 104, 112],
  "message": "文本 'SocialNetwork0' 推荐使用 96 位长度"
}
```

### 6. 下载文件 - GET /api/download/{filename}

下载处理后的图片文件。

## 💡 最佳实践

### 推荐的API使用顺序：

1. **添加水印**: 使用 `POST /api/watermark/add`
2. **检测水印**: 使用 `POST /api/watermark/detect` （**留空length参数**）
3. **如果检测失败**: 使用 `POST /api/watermark/scan` 扫描所有可能的水印
4. **精确提取**: 使用 `POST /api/watermark/extract` 和已知长度

### 关于length参数：

- ✅ **推荐**: 检测时留空length，让API智能推断
- ✅ **推荐**: 提取时留空length，使用默认96位
- ⚠️ **不推荐**: 手动猜测length值
- 💡 **提示**: 如果不确定，先用 `suggest-length` 获取建议

## 💻 NextJS前端使用示例

### 1. 添加水印示例

```typescript
// utils/watermarkApi.ts
const API_BASE = 'http://localhost:8000';

export async function addWatermark(imageFile: File, text: string, method = 'dwtDct') {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('text', text);
  formData.append('method', method);

  const response = await fetch(`${API_BASE}/api/watermark/add`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// 使用示例
const handleAddWatermark = async (file: File, watermarkText: string) => {
  try {
    const result = await addWatermark(file, watermarkText);
    if (result.success) {
      console.log('水印添加成功:', result.message);
      // 下载处理后的图片
      const downloadUrl = `${API_BASE}${result.download_url}`;
      window.open(downloadUrl, '_blank');
    } else {
      console.error('添加失败:', result.message);
    }
  } catch (error) {
    console.error('API调用失败:', error);
  }
};
```

### 2. 检测水印示例（智能长度推断）

```typescript
export async function detectWatermark(
  imageFile: File, 
  expectedWatermark: string, 
  method = 'dwtDct',
  length?: number  // 可选，不提供时使用智能推断
) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('watermark', expectedWatermark);
  formData.append('method', method);
  if (length) {
    formData.append('length', length.toString());
  }

  const response = await fetch(`${API_BASE}/api/watermark/detect`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
}

// 长度推荐功能
export async function suggestLength(text: string) {
  const formData = new FormData();
  formData.append('text', text);

  const response = await fetch(`${API_BASE}/api/watermark/suggest-length`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
}

// 使用示例 - 智能检测
const handleDetectWatermark = async (file: File, watermark: string) => {
  try {
    // 🧠 使用智能长度推断（推荐）
    const result = await detectWatermark(file, watermark);
    if (result.success) {
      if (result.has_watermark) {
        console.log(`✅ 检测到水印! 置信度: ${(result.confidence * 100).toFixed(1)}%`);
        console.log(`使用的长度: ${result.message}`);
      } else {
        console.log(`❌ 未检测到指定水印。解码内容: ${result.decoded_content}`);
      }
    }
  } catch (error) {
    console.error('检测失败:', error);
  }
};

// 使用示例 - 获取长度推荐
const handleGetLengthSuggestion = async (watermarkText: string) => {
  try {
    const result = await suggestLength(watermarkText);
    if (result.success) {
      console.log(`📏 推荐长度: ${result.recommended_length} 位`);
      console.log(`📋 建议尝试: ${result.suggested_lengths.join(', ')} 位`);
      console.log(`💡 ${result.message}`);
    }
  } catch (error) {
    console.error('获取推荐失败:', error);
  }
};
```

### 3. React组件示例

```tsx
// components/WatermarkTool.tsx
import React, { useState } from 'react';
import { addWatermark, detectWatermark } from '../utils/watermarkApi';

const WatermarkTool: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [watermarkText, setWatermarkText] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedLength, setSuggestedLength] = useState<number | null>(null);
  const [lengthInfo, setLengthInfo] = useState<string>('');

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleAddWatermark = async () => {
    if (!selectedFile || !watermarkText) {
      alert('请选择文件并输入水印文本');
      return;
    }

    setLoading(true);
    try {
      const result = await addWatermark(selectedFile, watermarkText);
      if (result.success) {
        alert('水印添加成功！');
        // 自动下载
        window.open(`http://localhost:8000${result.download_url}`, '_blank');
      } else {
        alert(`添加失败: ${result.message}`);
      }
    } catch (error) {
      alert('操作失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  const handleGetLengthSuggestion = async () => {
    if (!watermarkText) return;
    
    try {
      const result = await suggestLength(watermarkText);
      if (result.success) {
        setSuggestedLength(result.recommended_length);
        setLengthInfo(`推荐: ${result.recommended_length}位 | 候选: ${result.suggested_lengths.join(', ')}位`);
      }
    } catch (error) {
      console.error('获取长度推荐失败:', error);
    }
  };

  const handleDetectWatermark = async () => {
    if (!selectedFile || !watermarkText) {
      alert('请选择文件并输入水印文本');
      return;
    }

    setLoading(true);
    try {
      // 🧠 使用智能长度推断
      const result = await detectWatermark(selectedFile, watermarkText);
      if (result.success) {
        const message = result.has_watermark 
          ? `✅ 检测到水印! 置信度: ${(result.confidence * 100).toFixed(1)}%\n${result.message}`
          : `❌ 未检测到指定水印\n解码内容: ${result.decoded_content}`;
        alert(message);
      } else {
        alert(`检测失败: ${result.message}`);
      }
    } catch (error) {
      alert('操作失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-4">水印工具</h2>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          选择图片:
        </label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="w-full p-2 border border-gray-300 rounded"
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          水印文本:
        </label>
        <input
          type="text"
          value={watermarkText}
          onChange={(e) => {
            setWatermarkText(e.target.value);
            // 自动获取长度推荐
            if (e.target.value) {
              handleGetLengthSuggestion();
            }
          }}
          placeholder="输入水印内容"
          className="w-full p-2 border border-gray-300 rounded"
        />
        {lengthInfo && (
          <p className="text-sm text-gray-600 mt-1">
            🧠 {lengthInfo}
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleAddWatermark}
          disabled={loading}
          className="flex-1 bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? '处理中...' : '添加水印'}
        </button>
        
        <button
          onClick={handleDetectWatermark}
          disabled={loading}
          className="flex-1 bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 disabled:opacity-50"
        >
          {loading ? '检测中...' : '检测水印'}
        </button>
      </div>
    </div>
  );
};

export default WatermarkTool;
```

## 🔧 部署说明

### 开发环境
```bash
# 启动API开发服务器
python run_api.py
```

### 生产环境
```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn src.watermark.api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 或使用Uvicorn
uvicorn src.watermark.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## ⚠️ 重要约束和限制

### 文件和网络约束
- **支持的图片格式**: PNG, JPG, JPEG, BMP等常见格式
- **文件大小限制**: 建议小于10MB (未设置硬限制)
- **网络超时**: 大文件上传可能需要较长时间
- **临时文件**: 服务器会自动清理，但请及时下载结果

### API使用限制
- **并发限制**: 无特殊限制，但大量并发可能影响性能
- **速率限制**: 当前未设置，建议前端添加防抖
- **session**: 无状态API，每次请求独立

## 🛡️ 安全注意事项

1. **CORS配置**: 已配置支持localhost:3000，生产环境需调整
2. **文件验证**: API已包含基本的文件类型验证
3. **临时文件清理**: API会自动清理临时文件
4. **敏感信息**: 水印内容会在日志中显示，注意隐私
5. **HTTPS**: 生产环境建议使用HTTPS

## 📚 更多资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Uvicorn文档](https://www.uvicorn.org/)
- [NextJS文档](https://nextjs.org/docs)

## 🐛 常见问题和错误处理

### 常见错误及解决方案

#### 1. CORS错误
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```
**解决方案**: 确认API服务器正在运行，CORS已配置支持端口3000

#### 2. 422 Unprocessable Entity
```json
{"detail": [{"loc": ["body", "length"], "msg": "field required", "type": "value_error.missing"}]}
```
**解决方案**: 检查Form数据格式，确保所有必需字段都已提供

#### 3. 网络连接失败
```
TypeError: Failed to fetch
```
**解决方案**: 
- 确认API服务器正在运行: `curl http://localhost:8000/api/health`
- 检查网络连接
- 确认端口8000未被占用

#### 4. 文件上传失败
```json
{"success": false, "message": "请上传图片文件"}
```
**解决方案**: 
- 确认文件是图片格式
- 检查文件大小是否过大
- 确认FormData正确设置

### 调试技巧

1. **检查API状态**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **查看API文档**:
   访问 `http://localhost:8000/docs` 进行实时测试

3. **检查网络请求**:
   使用浏览器开发者工具的Network标签查看请求详情

4. **测试单个端点**:
   ```typescript
   // 简单的连接测试
   fetch('http://localhost:8000/')
     .then(res => res.json())
     .then(data => console.log('API连接正常:', data))
     .catch(err => console.error('API连接失败:', err));
   ```

## 📞 技术支持

如果遇到问题，请提供以下信息：
- 错误信息的完整截图
- 浏览器控制台的错误日志
- 网络请求的详细信息(Headers, Body等)
- 使用的图片文件信息(格式、大小等) 