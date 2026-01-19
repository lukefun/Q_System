"""
文档完整性属性测试

使用基于属性的测试验证系统的文档完整性
"""

import pytest
import inspect
import importlib
from pathlib import Path
from hypothesis import given, settings, strategies as st


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 获取所有源模块
def get_all_source_modules():
    """获取src目录下的所有Python模块"""
    src_path = Path('src')
    modules = []
    
    for py_file in src_path.glob('*.py'):
        if py_file.name != '__init__.py' and not py_file.name.startswith('_'):
            module_name = f"src.{py_file.stem}"
            modules.append(module_name)
    
    return modules


# 模块名称生成策略
@st.composite
def module_name_strategy(draw):
    """生成源模块名称"""
    modules = get_all_source_modules()
    if not modules:
        return None
    return draw(st.sampled_from(modules))


# ============================================================================
# 属性27：公共API文档完整性
# ============================================================================

class TestProperty27PublicAPIDocumentationCompleteness:
    """
    属性27：公共API文档完整性
    
    验证需求：10.1
    
    对于任何公共类和函数，都应该包含描述其功能、参数和返回值的文档字符串。
    """
    
    def get_public_members(self, module):
        """获取模块中的所有公共成员（类和函数）"""
        public_members = []
        
        for name, obj in inspect.getmembers(module):
            # 跳过私有成员和导入的成员
            if name.startswith('_'):
                continue
            
            # 检查是否是在当前模块中定义的
            if hasattr(obj, '__module__') and obj.__module__ != module.__name__:
                continue
            
            # 只检查类和函数
            if inspect.isclass(obj) or inspect.isfunction(obj):
                public_members.append((name, obj))
        
        return public_members
    
    def check_docstring_quality(self, obj, obj_name):
        """检查文档字符串的质量"""
        docstring = inspect.getdoc(obj)
        
        if not docstring:
            return False, f"{obj_name} 缺少文档字符串"
        
        # 检查文档字符串长度（至少应该有一些描述）
        if len(docstring.strip()) < 10:
            return False, f"{obj_name} 的文档字符串过于简短"
        
        # 对于函数，检查是否包含参数和返回值说明
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            # 获取函数签名
            try:
                sig = inspect.signature(obj)
                params = [p for p in sig.parameters.keys() if p not in ['self', 'cls']]
                
                # 如果有参数，文档应该提到参数
                if params and len(params) > 0:
                    docstring_lower = docstring.lower()
                    has_param_doc = any([
                        'args:' in docstring_lower,
                        'arguments:' in docstring_lower,
                        'parameters:' in docstring_lower,
                        '参数:' in docstring,
                        '参数：' in docstring
                    ])
                    
                    if not has_param_doc:
                        return False, f"{obj_name} 的文档缺少参数说明"
                
                # 如果有返回值（不是None），文档应该提到返回值
                if sig.return_annotation != inspect.Signature.empty:
                    docstring_lower = docstring.lower()
                    has_return_doc = any([
                        'returns:' in docstring_lower,
                        'return:' in docstring_lower,
                        '返回:' in docstring,
                        '返回：' in docstring
                    ])
                    
                    if not has_return_doc:
                        return False, f"{obj_name} 的文档缺少返回值说明"
            
            except (ValueError, TypeError):
                # 如果无法获取签名，跳过详细检查
                pass
        
        # 对于类，检查是否有类级别的文档
        if inspect.isclass(obj):
            # 类应该有描述
            if len(docstring.strip()) < 20:
                return False, f"{obj_name} 类的文档字符串过于简短"
        
        return True, ""
    
    @given(module_name=module_name_strategy())
    @settings(max_examples=20, deadline=None)
    def test_property_27_public_api_documentation_completeness(self, module_name):
        """
        Feature: week2-xtdata-engineering, Property 27: 公共API文档完整性
        
        验证：所有公共类和函数都有完整的文档字符串
        """
        if module_name is None:
            pytest.skip("没有找到源模块")
        
        # 导入模块
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            pytest.skip(f"无法导入模块 {module_name}: {e}")
        
        # 获取公共成员
        public_members = self.get_public_members(module)
        
        if not public_members:
            pytest.skip(f"模块 {module_name} 没有公共成员")
        
        # 检查每个公共成员的文档
        missing_docs = []
        poor_quality_docs = []
        
        for name, obj in public_members:
            is_good, message = self.check_docstring_quality(obj, f"{module_name}.{name}")
            
            if not is_good:
                if "缺少文档字符串" in message:
                    missing_docs.append(message)
                else:
                    poor_quality_docs.append(message)
        
        # 验证：所有公共API都应该有文档
        if missing_docs:
            pytest.fail(
                f"模块 {module_name} 中有 {len(missing_docs)} 个公共API缺少文档字符串:\n" +
                "\n".join(missing_docs)
            )
        
        # 验证：文档质量应该足够好
        if poor_quality_docs:
            pytest.fail(
                f"模块 {module_name} 中有 {len(poor_quality_docs)} 个公共API的文档质量不足:\n" +
                "\n".join(poor_quality_docs)
            )
    
    def test_all_modules_have_documentation(self):
        """
        验证：所有源模块都有完整的文档
        
        这是一个非基于属性的测试，用于全面检查所有模块
        """
        modules = get_all_source_modules()
        
        if not modules:
            pytest.skip("没有找到源模块")
        
        all_issues = {}
        
        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                all_issues[module_name] = [f"无法导入: {e}"]
                continue
            
            # 获取公共成员
            public_members = self.get_public_members(module)
            
            if not public_members:
                continue
            
            # 检查每个公共成员的文档
            module_issues = []
            
            for name, obj in public_members:
                is_good, message = self.check_docstring_quality(obj, f"{module_name}.{name}")
                
                if not is_good:
                    module_issues.append(message)
            
            if module_issues:
                all_issues[module_name] = module_issues
        
        # 生成报告
        if all_issues:
            report = ["文档完整性检查失败:\n"]
            for module_name, issues in all_issues.items():
                report.append(f"\n模块 {module_name}:")
                for issue in issues:
                    report.append(f"  - {issue}")
            
            pytest.fail("\n".join(report))
    
    def test_critical_classes_have_comprehensive_docs(self):
        """
        验证：关键类有全面的文档
        
        检查核心类是否有详细的文档，包括使用示例
        """
        critical_classes = [
            ('src.xtdata_client', 'XtDataClient'),
            ('src.data_retriever', 'DataRetriever'),
            ('src.price_adjuster', 'PriceAdjuster'),
            ('src.fundamental_handler', 'FundamentalHandler'),
            ('src.industry_mapper', 'IndustryMapper'),
            ('src.data_manager', 'DataManager'),
            ('src.visualizer', 'Visualizer'),
        ]
        
        issues = []
        
        for module_name, class_name in critical_classes:
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name, None)
                
                if cls is None:
                    issues.append(f"{module_name}.{class_name} 不存在")
                    continue
                
                # 检查类文档
                docstring = inspect.getdoc(cls)
                
                if not docstring:
                    issues.append(f"{module_name}.{class_name} 缺少文档字符串")
                    continue
                
                # 检查文档长度（关键类应该有详细文档）
                if len(docstring.strip()) < 50:
                    issues.append(f"{module_name}.{class_name} 的文档过于简短（少于50字符）")
                
                # 检查__init__方法的文档
                init_method = getattr(cls, '__init__', None)
                if init_method:
                    init_doc = inspect.getdoc(init_method)
                    if not init_doc or len(init_doc.strip()) < 20:
                        issues.append(f"{module_name}.{class_name}.__init__ 缺少或文档不足")
                
                # 检查公共方法的文档
                public_methods = [
                    name for name, method in inspect.getmembers(cls, predicate=inspect.isfunction)
                    if not name.startswith('_') or name == '__init__'
                ]
                
                for method_name in public_methods:
                    if method_name == '__init__':
                        continue
                    
                    method = getattr(cls, method_name)
                    method_doc = inspect.getdoc(method)
                    
                    if not method_doc:
                        issues.append(f"{module_name}.{class_name}.{method_name} 缺少文档字符串")
            
            except ImportError as e:
                issues.append(f"无法导入 {module_name}: {e}")
        
        if issues:
            pytest.fail(
                f"关键类的文档检查失败:\n" +
                "\n".join(f"  - {issue}" for issue in issues)
            )


# ============================================================================
# 额外的文档质量测试
# ============================================================================

class TestDocumentationQuality:
    """文档质量测试"""
    
    def test_module_level_docstrings(self):
        """验证：所有模块都有模块级文档字符串"""
        modules = get_all_source_modules()
        
        missing_module_docs = []
        
        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
                module_doc = inspect.getdoc(module)
                
                if not module_doc or len(module_doc.strip()) < 10:
                    missing_module_docs.append(module_name)
            
            except ImportError:
                continue
        
        if missing_module_docs:
            pytest.fail(
                f"以下模块缺少模块级文档字符串:\n" +
                "\n".join(f"  - {m}" for m in missing_module_docs)
            )
    
    def test_docstrings_use_consistent_format(self):
        """验证：文档字符串使用一致的格式"""
        modules = get_all_source_modules()
        
        inconsistent_formats = []
        
        for module_name in modules:
            try:
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module):
                    if name.startswith('_'):
                        continue
                    
                    if not (inspect.isclass(obj) or inspect.isfunction(obj)):
                        continue
                    
                    if hasattr(obj, '__module__') and obj.__module__ != module.__name__:
                        continue
                    
                    docstring = inspect.getdoc(obj)
                    
                    if not docstring:
                        continue
                    
                    # 检查是否使用了一致的参数格式
                    has_args_colon = 'Args:' in docstring or '参数:' in docstring or '参数：' in docstring
                    has_returns_colon = 'Returns:' in docstring or '返回:' in docstring or '返回：' in docstring
                    
                    # 如果使用了Args:格式，应该一致使用
                    if has_args_colon or has_returns_colon:
                        # 这是好的格式
                        continue
                    
                    # 检查是否有参数但没有使用标准格式
                    if inspect.isfunction(obj):
                        try:
                            sig = inspect.signature(obj)
                            params = [p for p in sig.parameters.keys() if p not in ['self', 'cls']]
                            
                            if params and len(params) > 0:
                                # 有参数但没有使用标准格式
                                if 'Args:' not in docstring and '参数:' not in docstring and '参数：' not in docstring:
                                    inconsistent_formats.append(f"{module_name}.{name}")
                        
                        except (ValueError, TypeError):
                            pass
            
            except ImportError:
                continue
        
        # 这个测试是警告性的，不强制失败
        if inconsistent_formats:
            print(f"\n警告：以下API的文档格式可能不一致:\n" +
                  "\n".join(f"  - {f}" for f in inconsistent_formats[:10]))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
