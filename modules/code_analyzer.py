"""模块2：代码仓库分析 - 自动分析项目结构、技术栈等"""

import os
import zipfile
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from git import Repo
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate


class CodeAnalyzer:
    """代码仓库分析器"""
    
    def __init__(self):
        self.llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.3
        )
        
    def _extract_zip(self, zip_path: str, extract_dir: str) -> str:
        """解压ZIP文件"""
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir
        
    def _clone_github(self, repo_url: str, clone_dir: str) -> str:
        """克隆GitHub仓库"""
        Repo.clone_from(repo_url, clone_dir)
        return clone_dir
        
    def _analyze_directory_structure(self, project_dir: str) -> List[str]:
        """分析目录结构"""
        structure = []
        project_path = Path(project_dir)
        
        def traverse(path: Path, level: int = 0):
            prefix = "  " * level
            if path.is_file():
                structure.append(f"{prefix}- {path.name}")
            else:
                structure.append(f"{prefix}+ {path.name}/")
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    if item.is_dir():
                        traverse(item, level + 1)
                    else:
                        structure.append(f"  {'  ' * level}- {item.name}")
                        
        traverse(project_path)
        return structure
        
    def _identify_tech_stack(self, project_dir: str) -> Dict[str, Any]:
        """识别技术栈"""
        tech_stack = {}
        project_path = Path(project_dir)
        
        # 检查常见配置文件
        config_files = {
            "Python": ["requirements.txt", "pyproject.toml", "setup.py"],
            "JavaScript/Node.js": ["package.json", "package-lock.json", "yarn.lock"],
            "Java": ["pom.xml", "build.gradle", "gradlew"],
            "Go": ["go.mod", "go.sum"],
            "Rust": ["Cargo.toml", "Cargo.lock"],
            "Docker": ["Dockerfile", "docker-compose.yml"]
        }
        
        for lang, files in config_files.items():
            for file in files:
                if (project_path / file).exists():
                    tech_stack["language"] = lang
                    tech_stack["config_file"] = file
                    
                    # 尝试解析依赖
                    if file == "package.json":
                        try:
                            with open(project_path / file, "r", encoding="utf-8") as f:
                                pkg = json.load(f)
                            tech_stack["dependencies"] = list(pkg.get("dependencies", {}).keys())
                            tech_stack["dev_dependencies"] = list(pkg.get("devDependencies", {}).keys())
                        except:
                            pass
                            
                    break
                    
        # 检查数据库相关文件
        db_files = ["db.sqlite", "database.yml", "schema.sql"]
        for file in db_files:
            if (project_path / file).exists():
                tech_stack["database"] = "SQL"
                
        return tech_stack
        
    def _analyze_readme(self, project_dir: str) -> str:
        """分析README文件"""
        project_path = Path(project_dir)
        readme_files = ["README.md", "README.txt", "README"]
        
        readme_content = ""
        for readme in readme_files:
            readme_path = project_path / readme
            if readme_path.exists():
                with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()
                break
                
        if not readme_content:
            return "未找到README文件"
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个项目文档解读专家。请分析以下README内容，用中文简洁地总结项目的功能、用途和主要特性。"),
            ("human", "{readme}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"readme": readme_content[:5000]})
        
        return response.content
        
    def _analyze_api_design(self, project_dir: str) -> str:
        """分析API接口设计"""
        project_path = Path(project_dir)
        api_patterns = [
            ("FastAPI", r"@app\.(get|post|put|delete|patch)"),
            ("Flask", r"@app\.route"),
            ("Django", r"url\(|path\("),
            ("Express", r"app\.(get|post|put|delete|patch)")
        ]
        
        api_files = []
        for file in project_path.rglob("*.py"):
            if file.name.startswith('.'):
                continue
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for framework, pattern in api_patterns:
                        if re.search(pattern, content):
                            api_files.append({
                                "file": str(file.relative_to(project_path)),
                                "framework": framework
                            })
                            break
            except:
                pass
                
        if not api_files:
            return "未检测到标准API路由定义"
            
        return "\n".join([f"- {f['file']} ({f['framework']})" for f in api_files])
        
    def _generate_architecture_diagram(self, structure: List[str], tech_stack: Dict[str, Any]) -> str:
        """使用Mermaid生成架构图"""
        mermaid_code = """```mermaid
graph TB
    subgraph 项目架构
        Root[项目根目录]
    """
        
        # 简化显示主要目录
        main_dirs = [s for s in structure if s.startswith('+ ')]
        for i, dir in enumerate(main_dirs[:8]):
            dir_name = dir.strip('+ ').rstrip('/')
            mermaid_code += f"        D{i}[{dir_name}] --> Root\n"
            
        mermaid_code += f"\n    subgraph 技术栈\n"
        if "language" in tech_stack:
            mermaid_code += f"        Lang[{tech_stack['language']}]\n"
        if "dependencies" in tech_stack:
            for dep in tech_stack["dependencies"][:5]:
                mermaid_code += f"        Dep_{dep}[{dep}]\n"
                
        mermaid_code += """    end
end
```"""
        
        return mermaid_code
        
    def analyze_project(self, source: str, source_type: str = "zip", project_name: str = "project") -> Dict[str, Any]:
        """分析项目
        
        Args:
            source: ZIP文件路径或GitHub仓库URL
            source_type: "zip" 或 "github"
            project_name: 项目名称
            
        Returns:
            分析结果字典
        """
        # 创建临时目录
        temp_dir = Path("./temp_projects")
        temp_dir.mkdir(exist_ok=True)
        
        project_dir = temp_dir / project_name
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
            
        # 处理项目源
        if source_type == "zip":
            self._extract_zip(source, str(project_dir))
        elif source_type == "github":
            self._clone_github(source, str(project_dir))
        else:
            return {"error": "不支持的源类型"}
            
        # 执行分析
        dir_structure = self._analyze_directory_structure(str(project_dir))
        tech_stack = self._identify_tech_stack(str(project_dir))
        readme_analysis = self._analyze_readme(str(project_dir))
        api_analysis = self._analyze_api_design(str(project_dir))
        architecture_diagram = self._generate_architecture_diagram(dir_structure, tech_stack)
        
        return {
            "project_name": project_name,
            "directory_structure": dir_structure,
            "tech_stack": tech_stack,
            "readme_analysis": readme_analysis,
            "api_analysis": api_analysis,
            "architecture_diagram": architecture_diagram
        }
        
    def generate_comprehensive_report(self, analysis_result: Dict[str, Any]) -> str:
        """生成综合分析报告"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个资深架构师。请基于以下项目分析信息，生成一份详细的中文项目分析报告。"),
            ("human", """项目分析信息：
项目名称: {project_name}
目录结构: {dir_structure}
技术栈: {tech_stack}
README分析: {readme_analysis}
API分析: {api_analysis}

请生成一份结构化的分析报告。""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "project_name": analysis_result["project_name"],
            "dir_structure": "\n".join(analysis_result["directory_structure"][:50]),
            "tech_stack": json.dumps(analysis_result["tech_stack"], ensure_ascii=False),
            "readme_analysis": analysis_result["readme_analysis"],
            "api_analysis": analysis_result["api_analysis"]
        })
        
        return response.content
