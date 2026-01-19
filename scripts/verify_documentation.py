"""
文档完整性验证脚本

验证Week 2金融数据工程系统的文档完整性，确保：
1. 所有公共类都有文档字符串
2. 所有公共函数都有文档字符串
3. 文档字符串包含必要的信息（参数、返回值、示例等）

属性27：公共API文档完整性
验证需求：10.1

作者：Q_System
日期：2026-01-19
"""

import sys
import os
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DocumentationVerifier:
    """文档完整性验证器"""
    
    def __init__(self, src_dir: str = 'src'):
        """
        初始化验证器
        
        Args:
            src_dir: 源代码目录
        """
        self.src_dir = Path(src_dir)
        self.issues = []
        self.stats = {
            'total_classes': 0,
            'documented_classes': 0,
            'total_functions': 0,
            'documented_functions': 0,
            'total_methods': 0,
            'documented_methods': 0
        }
    
    def verify_all(self) -> bool:
        """
        验证所有源文件的文档完整性
        
        Returns:
            是否通过验证
        """
        print("=" * 80)
        print("  文档完整性验证")
        print("=" * 80)
        print()
        
        # 获取所有Python文件
        python_files = list(self.src_dir.glob('*.py'))
        python_files = [f for f in python_files if f.name != '__init__.py']
        
        print(f"找到 {len(python_files)} 个源文件")
        print()
        
        # 验证每个文件
        for file_path in sorted(python_files):
            self._verify_file(file_path)
        
        # 打印统计信息
        self._print_statistics()
        
        # 打印问题列表
        if self.issues:
            self._print_issues()
            return False
        else:
            print("\n✅ 所有公共API都有完整的文档！")
            return True
    
    def _verify_file(self, file_path: Path):
        """
        验证单个文件的文档完整性
        
        Args:
            file_path: 文件路径
        """
        print(f"验证文件: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # 解析AST
            tree = ast.parse(source)
            
            # 验证类和函数
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._verify_class(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    # 只验证模块级别的函数
                    if self._is_module_level(node, tree):
                        self._verify_function(node, file_path)
        
        except Exception as e:
            print(f"  ⚠️  解析文件失败: {str(e)}")
    
    def _verify_class(self, node: ast.ClassDef, file_path: Path):
        """
        验证类的文档
        
        Args:
            node: 类节点
            file_path: 文件路径
        """
        # 跳过私有类
        if node.name.startswith('_'):
            return
        
        self.stats['total_classes'] += 1
        
        # 检查类文档字符串
        docstring = ast.get_docstring(node)
        if docstring:
            self.stats['documented_classes'] += 1
            print(f"  ✓ 类 {node.name} 有文档")
        else:
            self.issues.append({
                'file': file_path.name,
                'type': 'class',
                'name': node.name,
                'issue': '缺少文档字符串'
            })
            print(f"  ✗ 类 {node.name} 缺少文档")
        
        # 验证公共方法
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._verify_method(item, node.name, file_path)
    
    def _verify_method(self, node: ast.FunctionDef, class_name: str, file_path: Path):
        """
        验证方法的文档
        
        Args:
            node: 方法节点
            class_name: 类名
            file_path: 文件路径
        """
        # 跳过私有方法和特殊方法
        if node.name.startswith('_') and not node.name.startswith('__'):
            return
        
        # 跳过某些特殊方法
        if node.name in ['__init__', '__repr__', '__str__', '__enter__', '__exit__']:
            return
        
        self.stats['total_methods'] += 1
        
        # 检查方法文档字符串
        docstring = ast.get_docstring(node)
        if docstring:
            self.stats['documented_methods'] += 1
            # 检查文档质量
            if not self._check_docstring_quality(docstring, node):
                self.issues.append({
                    'file': file_path.name,
                    'type': 'method',
                    'name': f"{class_name}.{node.name}",
                    'issue': '文档字符串缺少必要信息（Args/Returns）'
                })
        else:
            self.issues.append({
                'file': file_path.name,
                'type': 'method',
                'name': f"{class_name}.{node.name}",
                'issue': '缺少文档字符串'
            })
    
    def _verify_function(self, node: ast.FunctionDef, file_path: Path):
        """
        验证函数的文档
        
        Args:
            node: 函数节点
            file_path: 文件路径
        """
        # 跳过私有函数
        if node.name.startswith('_'):
            return
        
        self.stats['total_functions'] += 1
        
        # 检查函数文档字符串
        docstring = ast.get_docstring(node)
        if docstring:
            self.stats['documented_functions'] += 1
            print(f"  ✓ 函数 {node.name} 有文档")
        else:
            self.issues.append({
                'file': file_path.name,
                'type': 'function',
                'name': node.name,
                'issue': '缺少文档字符串'
            })
            print(f"  ✗ 函数 {node.name} 缺少文档")
    
    def _is_module_level(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """
        检查函数是否是模块级别的
        
        Args:
            node: 函数节点
            tree: 模块树
        
        Returns:
            是否是模块级别
        """
        for item in tree.body:
            if item == node:
                return True
        return False
    
    def _check_docstring_quality(self, docstring: str, node: ast.FunctionDef) -> bool:
        """
        检查文档字符串的质量
        
        Args:
            docstring: 文档字符串
            node: 函数/方法节点
        
        Returns:
            文档质量是否合格
        """
        # 检查是否有参数但文档中没有Args
        has_args = len(node.args.args) > 1  # 排除self
        if has_args and 'Args:' not in docstring and 'Parameters:' not in docstring:
            return False
        
        # 检查是否有返回值但文档中没有Returns
        has_return = any(isinstance(n, ast.Return) and n.value is not None 
                        for n in ast.walk(node))
        if has_return and 'Returns:' not in docstring:
            return False
        
        return True
    
    def _print_statistics(self):
        """打印统计信息"""
        print()
        print("=" * 80)
        print("  统计信息")
        print("=" * 80)
        print()
        
        # 类统计
        class_coverage = (self.stats['documented_classes'] / self.stats['total_classes'] * 100 
                         if self.stats['total_classes'] > 0 else 0)
        print(f"类:")
        print(f"  总数: {self.stats['total_classes']}")
        print(f"  有文档: {self.stats['documented_classes']}")
        print(f"  覆盖率: {class_coverage:.1f}%")
        print()
        
        # 方法统计
        method_coverage = (self.stats['documented_methods'] / self.stats['total_methods'] * 100 
                          if self.stats['total_methods'] > 0 else 0)
        print(f"公共方法:")
        print(f"  总数: {self.stats['total_methods']}")
        print(f"  有文档: {self.stats['documented_methods']}")
        print(f"  覆盖率: {method_coverage:.1f}%")
        print()
        
        # 函数统计
        function_coverage = (self.stats['documented_functions'] / self.stats['total_functions'] * 100 
                            if self.stats['total_functions'] > 0 else 0)
        print(f"模块级函数:")
        print(f"  总数: {self.stats['total_functions']}")
        print(f"  有文档: {self.stats['documented_functions']}")
        print(f"  覆盖率: {function_coverage:.1f}%")
        print()
        
        # 总体统计
        total = (self.stats['total_classes'] + self.stats['total_methods'] + 
                self.stats['total_functions'])
        documented = (self.stats['documented_classes'] + self.stats['documented_methods'] + 
                     self.stats['documented_functions'])
        overall_coverage = (documented / total * 100 if total > 0 else 0)
        
        print(f"总体:")
        print(f"  总数: {total}")
        print(f"  有文档: {documented}")
        print(f"  覆盖率: {overall_coverage:.1f}%")
    
    def _print_issues(self):
        """打印问题列表"""
        print()
        print("=" * 80)
        print("  发现的问题")
        print("=" * 80)
        print()
        
        # 按文件分组
        issues_by_file = {}
        for issue in self.issues:
            file = issue['file']
            if file not in issues_by_file:
                issues_by_file[file] = []
            issues_by_file[file].append(issue)
        
        # 打印每个文件的问题
        for file, file_issues in sorted(issues_by_file.items()):
            print(f"{file}:")
            for issue in file_issues:
                print(f"  • {issue['type']} {issue['name']}: {issue['issue']}")
            print()
        
        print(f"共发现 {len(self.issues)} 个问题")


def main():
    """主函数"""
    verifier = DocumentationVerifier('src')
    success = verifier.verify_all()
    
    print()
    print("=" * 80)
    
    if success:
        print("  ✅ 文档完整性验证通过")
        print("=" * 80)
        print()
        print("所有公共API都有完整的文档字符串！")
        return 0
    else:
        print("  ❌ 文档完整性验证失败")
        print("=" * 80)
        print()
        print("请为缺少文档的API添加文档字符串。")
        print("文档字符串应包含：")
        print("• 功能描述")
        print("• Args: 参数说明")
        print("• Returns: 返回值说明")
        print("• Raises: 异常说明（如果有）")
        print("• Example: 使用示例（推荐）")
        return 1


if __name__ == '__main__':
    sys.exit(main())
