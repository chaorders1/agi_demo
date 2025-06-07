# 🚀 前端工程师快速接入指南

## 📋 TL;DR (太长不看版)

```typescript
// 1. 基础配置
const API_BASE = 'http://localhost:8000';

// 2. 添加水印
const addWatermark = async (imageFile: File, text: string) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('text', text);
  
  const response = await fetch(`${API_BASE}/api/watermark/add`, {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
};

// 3. 检测水印 (推荐不填length，使用智能推断)
const detectWatermark = async (imageFile: File, watermark: string) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('watermark', watermark);
  // 不添加length字段，让API智能推断
  
  const response = await fetch(`${API_BASE}/api/watermark/detect`, {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
};
```

## ✅ 前置检查

1. **API服务器状态**: 
   ```bash
   curl http://localhost:8000/api/health
   # 应该返回: {"status":"healthy","message":"Watermark API is running"}
   ```

2. **CORS检查**: 在浏览器控制台运行
   ```javascript
   fetch('http://localhost:8000/')
     .then(res => res.json())
     .then(data => console.log('✅ API连接正常:', data))
     .catch(err => console.error('❌ 连接失败:', err));
   ```

## 🎯 核心API接口

### 添加水印
```typescript
POST /api/watermark/add
FormData: {
  image: File,        // 图片文件
  text: string,       // 水印文本
  method?: "dwtDct"   // 可选，默认dwtDct
}
```

### 检测水印 (推荐)
```typescript
POST /api/watermark/detect
FormData: {
  image: File,         // 图片文件
  watermark: string,   // 期望的水印内容
  method?: "dwtDct",   // 可选，默认dwtDct
  // length: 不填写，使用智能推断 🧠
}
```

### 扫描未知水印
```typescript
POST /api/watermark/scan
FormData: {
  image: File,           // 图片文件
  method?: "dwtDct",     // 可选，默认dwtDct
  max_length?: 512,      // 可选，最大长度
  verbose?: false        // 可选，详细信息
}
```

## 📦 完整工具类

```typescript
// utils/watermarkApi.ts
const API_BASE = 'http://localhost:8000';

interface WatermarkResponse {
  success: boolean;
  message: string;
  [key: string]: any;
}

export class WatermarkAPI {
  
  // 添加水印
  static async addWatermark(imageFile: File, text: string): Promise<WatermarkResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('text', text);

    const response = await fetch(`${API_BASE}/api/watermark/add`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  // 检测水印 (智能推断)
  static async detectWatermark(imageFile: File, watermark: string): Promise<WatermarkResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('watermark', watermark);

    const response = await fetch(`${API_BASE}/api/watermark/detect`, {
      method: 'POST',
      body: formData,
    });

    return await response.json();
  }

  // 扫描所有水印
  static async scanWatermarks(imageFile: File): Promise<WatermarkResponse> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${API_BASE}/api/watermark/scan`, {
      method: 'POST',
      body: formData,
    });

    return await response.json();
  }

  // 获取长度建议
  static async suggestLength(text: string): Promise<WatermarkResponse> {
    const formData = new FormData();
    formData.append('text', text);

    const response = await fetch(`${API_BASE}/api/watermark/suggest-length`, {
      method: 'POST',
      body: formData,
    });

    return await response.json();
  }

  // 下载处理后的图片
  static getDownloadUrl(filename: string): string {
    return `${API_BASE}/api/download/${filename}`;
  }

  // 健康检查
  static async healthCheck(): Promise<any> {
    const response = await fetch(`${API_BASE}/api/health`);
    return await response.json();
  }
}
```

## 🎨 React Hook示例

```typescript
// hooks/useWatermark.ts
import { useState } from 'react';
import { WatermarkAPI } from '../utils/watermarkApi';

export const useWatermark = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addWatermark = async (file: File, text: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await WatermarkAPI.addWatermark(file, text);
      
      if (result.success) {
        // 自动下载
        const downloadUrl = WatermarkAPI.getDownloadUrl(result.output_filename);
        window.open(downloadUrl, '_blank');
        return result;
      } else {
        throw new Error(result.message);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '操作失败';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const detectWatermark = async (file: File, watermark: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await WatermarkAPI.detectWatermark(file, watermark);
      
      if (result.success) {
        return {
          hasWatermark: result.has_watermark,
          confidence: result.confidence,
          message: result.message
        };
      } else {
        throw new Error(result.message);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '检测失败';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    addWatermark,
    detectWatermark,
  };
};
```

## 🚨 常见错误处理

```typescript
// 错误处理包装器
const handleApiCall = async <T>(apiCall: () => Promise<T>): Promise<T> => {
  try {
    return await apiCall();
  } catch (error) {
    console.error('API调用失败:', error);
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('🔌 API服务器连接失败，请检查服务器是否启动');
    }
    
    if (error instanceof Error && error.message.includes('422')) {
      throw new Error('📋 请求参数错误，请检查表单数据');
    }
    
    throw error;
  }
};

// 使用示例
const result = await handleApiCall(() => 
  WatermarkAPI.addWatermark(file, text)
);
```

## 💡 最佳实践

1. **🧠 智能推断**: 检测水印时不要填写length参数
2. **⚡ 性能优化**: 大文件上传前先压缩
3. **🔄 重试机制**: 网络错误时自动重试
4. **📱 用户体验**: 显示上传进度和加载状态
5. **🛡️ 错误处理**: 提供友好的错误提示

## 🔗 相关链接

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health
- **详细文档**: [api_usage.md](./api_usage.md) 