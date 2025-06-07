#!/usr/bin/env python
"""
FastAPI REST API for watermark functionality
提供水印添加、检测、提取和扫描的RESTful API接口
"""

import os
import tempfile
import uuid
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import shutil

from .core import add_watermark, extract_watermark
from .detector import detect_watermark, extract_any_watermark


# FastAPI应用实例
app = FastAPI(
    title="Invisible Watermark API",
    description="A RESTful API for adding, detecting, and extracting invisible watermarks in images",
    version="1.0.0"
)

# 配置CORS中间件，允许NextJS前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # NextJS默认端口
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 临时文件存储目录
TEMP_DIR = os.path.join(tempfile.gettempdir(), "watermark_api")
os.makedirs(TEMP_DIR, exist_ok=True)


# Pydantic模型定义
class WatermarkAddResponse(BaseModel):
    """添加水印响应模型"""
    success: bool
    message: str
    output_filename: Optional[str] = None
    download_url: Optional[str] = None


class WatermarkDetectResponse(BaseModel):
    """检测水印响应模型"""
    success: bool
    has_watermark: Optional[bool] = None
    confidence: Optional[float] = None
    decoded_content: Optional[str] = None
    message: str



class WatermarkExtractResponse(BaseModel):
    """提取水印响应模型"""
    success: bool
    watermark_content: Optional[str] = None
    message: str


class WatermarkScanResult(BaseModel):
    """扫描结果项模型"""
    length: int
    content: str
    raw_bytes: Optional[str] = None


class WatermarkScanResponse(BaseModel):
    """扫描水印响应模型"""
    success: bool
    found_watermarks: List[WatermarkScanResult]
    message: str


def save_temp_file(file: UploadFile) -> str:
    """保存上传文件到临时目录"""
    file_extension = os.path.splitext(file.filename)[1] if file.filename else '.png'
    temp_filename = f"{uuid.uuid4()}{file_extension}"
    temp_path = os.path.join(TEMP_DIR, temp_filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return temp_path


def generate_output_filename(input_filename: str, suffix: str = "_watermarked") -> str:
    """生成输出文件名"""
    name_without_ext, ext = os.path.splitext(input_filename)
    return f"{name_without_ext}{suffix}{ext}"


def calculate_watermark_length(text: str) -> int:
    """
    智能计算水印长度(位)
    根据文本内容和常见长度模式自动推断
    """
    # 基础计算：UTF-8编码长度 * 8
    byte_length = len(text.encode('utf-8'))
    bit_length = byte_length * 8
    
    # 常见的水印长度模式（位）
    common_lengths = [32, 64, 96, 128, 160, 192, 224, 256]
    
    # 如果计算出的长度是常见长度，直接返回
    if bit_length in common_lengths:
        return bit_length
    
    # 找到最接近的常见长度
    closest_length = min(common_lengths, key=lambda x: abs(x - bit_length))
    
    # 如果差距很小（<=16位，即2字节），使用常见长度
    if abs(closest_length - bit_length) <= 16:
        return closest_length
    
    # 否则使用计算出的长度
    return bit_length


def get_suggested_lengths(text: str) -> List[int]:
    """
    获取建议的长度列表，用于多次尝试检测
    """
    base_length = calculate_watermark_length(text)
    
    # 生成候选长度列表
    suggested = [base_length]
    
    # 添加基于文本长度的其他可能长度
    byte_length = len(text.encode('utf-8'))
    alternative_lengths = [
        byte_length * 8,  # 精确长度
        (byte_length + 1) * 8,  # 可能有padding
        (byte_length - 1) * 8 if byte_length > 1 else 8,  # 可能被截断
    ]
    
    # 添加常见长度
    common_lengths = [32, 64, 96, 128, 160, 192, 224, 256]
    
    # 合并并去重
    all_lengths = suggested + alternative_lengths + common_lengths
    unique_lengths = sorted(list(set(l for l in all_lengths if l > 0)))
    
    # 返回前5个最可能的长度
    return unique_lengths[:5]


@app.get("/")
async def root():
    """API根端点"""
    return {
        "message": "Invisible Watermark API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/watermark/add - Add watermark to image",
            "POST /api/watermark/detect - Detect specific watermark (智能长度推断)",
            "POST /api/watermark/extract - Extract watermark with known length",
            "POST /api/watermark/scan - Scan for any watermarks",
            "POST /api/watermark/suggest-length - Get recommended length for text",
            "GET /api/download/{filename} - Download processed image"
        ],
        "features": [
            "🧠 智能长度推断 - 自动计算最佳水印长度",
            "🔄 多长度尝试 - 自动尝试多种可能的长度",
            "📊 置信度评分 - 提供检测结果的可信度",
            "🎯 模糊匹配 - 支持相似度匹配，提高容错性"
        ]
    }


@app.post("/api/watermark/add", response_model=WatermarkAddResponse)
async def add_watermark_endpoint(
    image: UploadFile = File(..., description="Input image file"),
    text: str = Form(..., description="Watermark text to embed"),
    method: str = Form(default="dwtDct", description="Watermarking method (dwtDct or rivaGan)")
):
    """
    添加不可见水印到图片
    
    - **image**: 输入图片文件 (支持PNG, JPG, JPEG等格式)
    - **text**: 要嵌入的水印文本
    - **method**: 水印算法 (dwtDct 或 rivaGan, 默认dwtDct)
    """
    try:
        # 验证输入参数
        if not text.strip():
            raise HTTPException(status_code=400, detail="水印文本不能为空")
        
        if method not in ["dwtDct", "rivaGan"]:
            raise HTTPException(status_code=400, detail="不支持的水印算法")
        
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图片文件")
        
        # 保存上传的图片
        input_path = save_temp_file(image)
        
        # 生成输出文件路径
        output_filename = generate_output_filename(image.filename or "image.png")
        output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_{output_filename}")
        
        # 添加水印
        add_watermark(input_path, output_path, text, method)
        
        # 清理输入临时文件
        os.unlink(input_path)
        
        return WatermarkAddResponse(
            success=True,
            message="水印添加成功",
            output_filename=os.path.basename(output_path),
            download_url=f"/api/download/{os.path.basename(output_path)}"
        )
        
    except Exception as e:
        return WatermarkAddResponse(
            success=False,
            message=f"添加水印失败: {str(e)}"
        )


@app.post("/api/watermark/detect", response_model=WatermarkDetectResponse)
async def detect_watermark_endpoint(
    image: UploadFile = File(..., description="Watermarked image file"),
    watermark: str = Form(..., description="Expected watermark content"),
    method: str = Form(default="dwtDct", description="Watermarking method"),
    length: Optional[int] = Form(default=None, description="Watermark length in bits (留空使用智能推断)", example=None)
):
    """
    检测图片中是否包含指定的水印内容 🧠 智能检测
    
    - **image**: 待检测的图片文件
    - **watermark**: 期望的水印内容
    - **method**: 水印算法 (默认dwtDct)
    - **length**: 水印长度(位)，留空使用智能推断，自动尝试多种长度
    
    💡 推荐不填写length参数，让API自动推断最佳长度
    """
    try:
        # 验证输入参数
        if not watermark.strip():
            raise HTTPException(status_code=400, detail="水印内容不能为空")
        
        if method not in ["dwtDct", "rivaGan"]:
            raise HTTPException(status_code=400, detail="不支持的水印算法")
        
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图片文件")
        
        # 保存上传的图片
        input_path = save_temp_file(image)
        
        try:
            # 智能检测水印
            if length is None or length == 0:
                # 使用智能长度推断和多次尝试
                suggested_lengths = get_suggested_lengths(watermark)
                best_result = None
                best_confidence = 0.0
                
                for try_length in suggested_lengths:
                    has_watermark, confidence, decoded = detect_watermark(
                        input_path, method, watermark, try_length
                    )
                    
                    # 如果找到匹配，优先选择置信度最高的
                    if has_watermark and (best_result is None or confidence > best_confidence):
                        best_result = (has_watermark, confidence, decoded, try_length)
                        best_confidence = confidence
                    
                    # 如果置信度很高，直接返回
                    if confidence and confidence > 0.9:
                        break
                
                # 如果没有找到匹配，返回置信度最高的结果
                if best_result is None:
                    # 使用第一个长度的结果
                    has_watermark, confidence, decoded = detect_watermark(
                        input_path, method, watermark, suggested_lengths[0]
                    )
                    message = f"检测完成 (尝试了 {len(suggested_lengths)} 种长度，建议长度: {suggested_lengths[0]} 位)"
                else:
                    has_watermark, confidence, decoded, used_length = best_result
                    message = f"检测完成 (使用长度: {used_length} 位)"
            else:
                # 使用指定长度
                has_watermark, confidence, decoded = detect_watermark(
                    input_path, method, watermark, length
                )
                message = f"检测完成 (使用指定长度: {length} 位)"
            
            return WatermarkDetectResponse(
                success=True,
                has_watermark=has_watermark,
                confidence=confidence,
                decoded_content=decoded,
                message=message
            )
            
        finally:
            # 清理临时文件
            os.unlink(input_path)
            
    except Exception as e:
        return WatermarkDetectResponse(
            success=False,
            message=f"检测失败: {str(e)}"
        )


@app.post("/api/watermark/extract", response_model=WatermarkExtractResponse)
async def extract_watermark_endpoint(
    image: UploadFile = File(..., description="Watermarked image file"),
    length: Optional[int] = Form(default=None, description="Watermark length in bits (留空使用默认96位)", example=None),
    method: str = Form(default="dwtDct", description="Watermarking method")
):
    """
    从图片中提取指定长度的水印内容
    
    - **image**: 包含水印的图片文件
    - **length**: 水印长度(位)，留空使用默认96位
    - **method**: 水印算法 (默认dwtDct)
    
    💡 如果不确定长度，建议先使用 scan 接口扫描
    """
    try:
        # 设置默认长度
        if length is None or length == 0:
            length = 96  # 常见的默认长度，适合大多数水印文本(12字节)
        
        # 验证输入参数
        if length <= 0:
            raise HTTPException(status_code=400, detail="水印长度必须大于0")
        
        if method not in ["dwtDct", "rivaGan"]:
            raise HTTPException(status_code=400, detail="不支持的水印算法")
        
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图片文件")
        
        # 保存上传的图片
        input_path = save_temp_file(image)
        
        try:
            # 提取水印
            watermark_content = extract_watermark(input_path, length, method)
            
            return WatermarkExtractResponse(
                success=True,
                watermark_content=watermark_content,
                message=f"水印提取成功 (使用长度: {length} 位)"
            )
            
        finally:
            # 清理临时文件
            os.unlink(input_path)
            
    except Exception as e:
        return WatermarkExtractResponse(
            success=False,
            message=f"提取失败: {str(e)}"
        )


@app.post("/api/watermark/scan", response_model=WatermarkScanResponse)
async def scan_watermarks_endpoint(
    image: UploadFile = File(..., description="Image file to scan"),
    method: str = Form(default="dwtDct", description="Watermarking method"),
    max_length: int = Form(default=512, description="Maximum watermark length to try"),
    verbose: bool = Form(default=False, description="Include raw bytes in response")
):
    """
    扫描图片中可能存在的任何水印内容
    
    - **image**: 待扫描的图片文件
    - **method**: 水印算法 (默认dwtDct)
    - **max_length**: 最大尝试长度(位) (默认512)
    - **verbose**: 是否包含原始字节数据
    """
    try:
        # 验证输入参数
        if max_length <= 0 or max_length > 2048:
            raise HTTPException(status_code=400, detail="最大长度必须在1-2048之间")
        
        if method not in ["dwtDct", "rivaGan"]:
            raise HTTPException(status_code=400, detail="不支持的水印算法")
        
        # 验证文件类型
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图片文件")
        
        # 保存上传的图片
        input_path = save_temp_file(image)
        
        try:
            # 扫描水印
            found_watermarks = extract_any_watermark(input_path, method, max_length)
            
            # 转换为响应格式
            scan_results = []
            for wm in found_watermarks:
                result = WatermarkScanResult(
                    length=wm['length'],
                    content=wm['content']
                )
                if verbose and 'raw_bytes' in wm:
                    result.raw_bytes = wm['raw_bytes'].hex() if isinstance(wm['raw_bytes'], bytes) else str(wm['raw_bytes'])
                scan_results.append(result)
            
            return WatermarkScanResponse(
                success=True,
                found_watermarks=scan_results,
                message=f"扫描完成，发现 {len(scan_results)} 个可能的水印"
            )
            
        finally:
            # 清理临时文件
            os.unlink(input_path)
            
    except Exception as e:
        return WatermarkScanResponse(
            success=False,
            found_watermarks=[],
            message=f"扫描失败: {str(e)}"
        )


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    下载处理后的图片文件
    
    - **filename**: 文件名
    """
    file_path = os.path.join(TEMP_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='image/png'
    )


@app.post("/api/watermark/suggest-length")
async def suggest_length_endpoint(
    text: str = Form(..., description="Watermark text to calculate length for")
):
    """
    根据水印文本推荐合适的长度
    
    - **text**: 水印文本
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="水印文本不能为空")
        
        # 计算推荐长度
        recommended_length = calculate_watermark_length(text)
        suggested_lengths = get_suggested_lengths(text)
        
        return {
            "success": True,
            "text": text,
            "text_byte_length": len(text.encode('utf-8')),
            "recommended_length": recommended_length,
            "suggested_lengths": suggested_lengths,
            "message": f"文本 '{text}' 推荐使用 {recommended_length} 位长度"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"计算失败: {str(e)}"
        }


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "message": "Watermark API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 