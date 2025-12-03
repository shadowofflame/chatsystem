"""
Agent工具集
提供文件处理、网络搜索等工具
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import mimetypes
from datetime import datetime


class FileHandler:
    """文件处理工具"""
    
    def __init__(self, workspace_dir: str = "./workspace"):
        """
        初始化文件处理器
        
        Args:
            workspace_dir: 工作空间目录
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def _resolve_filepath(self, filepath: str) -> Path:
        """
        解析文件路径，处理各种路径格式
        
        Args:
            filepath: 文件路径（可以是绝对路径或相对路径）
            
        Returns:
            解析后的 Path 对象
        """
        file_path = Path(filepath)
        
        # 如果是绝对路径且存在，直接返回
        if file_path.is_absolute() and file_path.exists():
            return file_path
        
        # 如果路径以 workspace 开头，去掉前缀
        filepath_str = str(filepath).replace("\\", "/")
        if filepath_str.startswith("workspace/"):
            filepath_str = filepath_str[len("workspace/"):]
        elif filepath_str.startswith("./workspace/"):
            filepath_str = filepath_str[len("./workspace/"):]
        
        # 相对于 workspace 目录
        resolved_path = self.workspace_dir / filepath_str
        
        return resolved_path
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        读取文件内容
        
        Args:
            filepath: 文件路径
            
        Returns:
            {success: bool, content: str, error: str}
        """
        try:
            file_path = self._resolve_filepath(filepath)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {filepath}"
                }
            
            # 根据文件类型读取
            mime_type, _ = mimetypes.guess_type(str(file_path))
            suffix = file_path.suffix.lower()
            
            # 常见文本文件扩展名
            text_extensions = {'.txt', '.md', '.py', '.java', '.js', '.ts', '.html', '.css', 
                            '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log',
                            '.csv', '.sql', '.sh', '.bat', '.ps1', '.vue', '.jsx', '.tsx'}
            
            if suffix in text_extensions or (mime_type and mime_type.startswith('text')):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                # 二进制文件返回文件信息
                file_size = file_path.stat().st_size
                content = f"二进制文件，大小: {file_size} 字节"
            
            return {
                "success": True,
                "content": content,
                "filepath": str(file_path),
                "size": file_path.stat().st_size
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"读取文件失败: {str(e)}"
            }
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        写入文件
        
        Args:
            filepath: 文件路径
            content: 文件内容
            
        Returns:
            {success: bool, filepath: str, error: str}
        """
        try:
            file_path = self.workspace_dir / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": str(file_path),
                "size": file_path.stat().st_size
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"写入文件失败: {str(e)}"
            }
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            
        Returns:
            {success: bool, files: List[str], error: str}
        """
        try:
            dir_path = self.workspace_dir / directory
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"目录不存在: {directory}"
                }
            
            files = []
            for item in dir_path.iterdir():
                file_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                }
                files.append(file_info)
            
            return {
                "success": True,
                "files": files,
                "directory": str(dir_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"列出文件失败: {str(e)}"
            }
    
    def delete_file(self, filepath: str) -> Dict[str, Any]:
        """
        删除文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            {success: bool, error: str}
        """
        try:
            file_path = self.workspace_dir / filepath
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {filepath}"
                }
            
            file_path.unlink()
            
            return {
                "success": True,
                "message": f"文件已删除: {filepath}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"删除文件失败: {str(e)}"
            }
    
    def save_uploaded_file(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        保存上传的文件
        
        Args:
            filename: 文件名
            content: 文件二进制内容
            
        Returns:
            {success: bool, filepath: str, size: int, error: str}
        """
        try:
            # 创建 uploads 子目录
            uploads_dir = self.workspace_dir / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # 添加时间戳避免文件名冲突
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            file_path = uploads_dir / safe_filename
            
            # 写入二进制内容
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return {
                "success": True,
                "filepath": str(file_path.absolute()),  # 返回绝对路径
                "filename": safe_filename,
                "original_name": filename,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"保存上传文件失败: {str(e)}"
            }
    
    def read_uploaded_file_content(self, filepath: str) -> Dict[str, Any]:
        """
        读取上传文件的内容（用于AI分析）
        
        Args:
            filepath: 文件路径（可以是绝对路径或相对于workspace的路径）
            
        Returns:
            {success: bool, content: str, file_type: str, error: str}
        """
        try:
            file_path = self._resolve_filepath(filepath)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {filepath}"
                }
            
            # 获取文件类型
            mime_type, _ = mimetypes.guess_type(str(file_path))
            suffix = file_path.suffix.lower()
            
            # 文本文件
            text_extensions = {'.txt', '.md', '.py', '.java', '.js', '.ts', '.html', '.css', 
                            '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log',
                            '.csv', '.sql', '.sh', '.bat', '.ps1', '.vue', '.jsx', '.tsx'}
            
            if suffix in text_extensions or (mime_type and mime_type.startswith('text')):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return {
                    "success": True,
                    "content": content,
                    "file_type": "text",
                    "mime_type": mime_type or "text/plain"
                }
            
            # PDF文件 - 需要额外库
            elif suffix == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page in pdf_reader.pages:
                            content += page.extract_text() + "\n"
                    return {
                        "success": True,
                        "content": content,
                        "file_type": "pdf",
                        "pages": len(pdf_reader.pages)
                    }
                except ImportError:
                    return {
                        "success": True,
                        "content": f"[PDF文件: {file_path.name}，需要安装PyPDF2来读取内容]",
                        "file_type": "pdf"
                    }
            
            # Word文档
            elif suffix in {'.docx', '.doc'}:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    content = "\n".join([para.text for para in doc.paragraphs])
                    return {
                        "success": True,
                        "content": content,
                        "file_type": "word"
                    }
                except ImportError:
                    return {
                        "success": True,
                        "content": f"[Word文件: {file_path.name}，需要安装python-docx来读取内容]",
                        "file_type": "word"
                    }
            
            # 图片文件
            elif suffix in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}:
                file_size = file_path.stat().st_size
                return {
                    "success": True,
                    "content": f"[图片文件: {file_path.name}，大小: {file_size} 字节]",
                    "file_type": "image",
                    "size": file_size
                }
            
            # 其他二进制文件
            else:
                file_size = file_path.stat().st_size
                return {
                    "success": True,
                    "content": f"[二进制文件: {file_path.name}，类型: {mime_type or '未知'}，大小: {file_size} 字节]",
                    "file_type": "binary",
                    "size": file_size
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"读取文件失败: {str(e)}"
            }


class WebSearcher:
    """网络搜索工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化网络搜索器
        
        Args:
            api_key: 搜索API密钥（如Serper API）
        """
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.serper_url = "https://google.serper.dev/search"
    
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            {success: bool, results: List[Dict], error: str}
        """
        if not self.api_key:
            return self._duckduckgo_search(query, num_results)
        
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results
            }
            
            response = requests.post(
                self.serper_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('organic', [])[:num_results]:
                results.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "snippet": item.get('snippet', '')
                })
            
            return {
                "success": True,
                "results": results,
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}",
                "fallback": "尝试使用备用搜索方法"
            }
    
    def _duckduckgo_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        使用DuckDuckGo进行搜索（备用方案）
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for i, result in enumerate(ddgs.text(query, max_results=num_results)):
                    if i >= num_results:
                        break
                    results.append({
                        "title": result.get('title', ''),
                        "link": result.get('href', ''),
                        "snippet": result.get('body', '')
                    })
            
            return {
                "success": True,
                "results": results,
                "query": query,
                "source": "DuckDuckGo"
            }
        except ImportError:
            return {
                "success": False,
                "error": "未安装 duckduckgo-search 库，请运行: pip install duckduckgo-search"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"DuckDuckGo搜索失败: {str(e)}"
            }
    
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        获取URL内容
        
        Args:
            url: 网页URL
            
        Returns:
            {success: bool, content: str, error: str}
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 简单提取文本内容
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # 限制长度
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return {
                "success": True,
                "content": text,
                "url": url
            }
        except ImportError:
            return {
                "success": False,
                "error": "未安装 beautifulsoup4 库，请运行: pip install beautifulsoup4"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取URL内容失败: {str(e)}"
            }


class Calculator:
    """计算器工具"""
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """
        执行数学计算
        
        Args:
            expression: 数学表达式
            
        Returns:
            {success: bool, result: float, error: str}
        """
        try:
            # 安全的数学表达式求值
            allowed_names = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow
            }
            
            # 移除危险字符
            if any(char in expression for char in ['__', 'import', 'eval', 'exec']):
                return {
                    "success": False,
                    "error": "表达式包含不安全的操作"
                }
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return {
                "success": True,
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"计算失败: {str(e)}"
            }
