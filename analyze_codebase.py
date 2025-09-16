#!/usr/bin/env python3
"""
Safe Codebase Analysis Tool
Analyzes the codebase without modifying anything
"""

import os
import sys
import ast
import json
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeCodebaseAnalyzer:
    """Analyze codebase without modifying anything"""
    
    def __init__(self, src_path="src"):
        self.src_path = Path(src_path)
        self.analysis = {
            'total_files': 0,
            'file_types': defaultdict(int),
            'imports': defaultdict(set),
            'functions': defaultdict(list),
            'classes': defaultdict(list),
            'file_sizes': {},
            'potential_duplicates': [],
            'unused_files': [],
            'main_modules': [],
            'backup_files': [],
            'test_files': [],
            'config_files': [],
            'service_files': [],
            'route_files': []
        }
    
    def analyze_file_structure(self):
        """Analyze file structure and categorize files"""
        logger.info("🔍 Analyzing file structure...")
        
        for py_file in self.src_path.rglob("*.py"):
            self.analysis['total_files'] += 1
            
            # Get file info
            file_size = py_file.stat().st_size
            self.analysis['file_sizes'][str(py_file)] = file_size
            
            # Categorize files
            file_name = py_file.name.lower()
            file_path = str(py_file.relative_to(self.src_path))
            
            # Identify file types
            if any(suffix in file_name for suffix in ['_backup', '_clean', '_fixed', '_old']):
                self.analysis['backup_files'].append(file_path)
            elif file_name.startswith('test_'):
                self.analysis['test_files'].append(file_path)
            elif 'config' in file_path:
                self.analysis['config_files'].append(file_path)
            elif 'services' in file_path:
                self.analysis['service_files'].append(file_path)
            elif 'routes' in file_path:
                self.analysis['route_files'].append(file_path)
            elif file_name in ['main_app.py', 'app.py', 'run_dashboard.py', '__init__.py']:
                self.analysis['main_modules'].append(file_path)
    
    def analyze_imports_and_functions(self):
        """Analyze imports and function definitions"""
        logger.info("🔍 Analyzing imports and functions...")
        
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content, filename=str(py_file))
                except SyntaxError:
                    logger.warning(f"⚠️ Syntax error in {py_file}")
                    continue
                
                file_path = str(py_file.relative_to(self.src_path))
                
                # Analyze imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.analysis['imports'][file_path].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.analysis['imports'][file_path].add(node.module)
                    elif isinstance(node, ast.FunctionDef):
                        self.analysis['functions'][file_path].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        self.analysis['classes'][file_path].append(node.name)
                        
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing {py_file}: {e}")
    
    def find_potential_duplicates(self):
        """Find potential duplicate files based on function names"""
        logger.info("🔍 Finding potential duplicates...")
        
        function_to_files = defaultdict(list)
        
        # Map functions to files
        for file_path, functions in self.analysis['functions'].items():
            for func in functions:
                if not func.startswith('_') and len(func) > 3:  # Skip private/short functions
                    function_to_files[func].append(file_path)
        
        # Find potential duplicates
        for func, files in function_to_files.items():
            if len(files) > 1 and func not in ['main', 'init', 'setup']:  # Skip common function names
                self.analysis['potential_duplicates'].append({
                    'function': func,
                    'files': files
                })
    
    def identify_unused_files(self):
        """Identify potentially unused files (basic heuristic)"""
        logger.info("🔍 Identifying potentially unused files...")
        
        # This is a simple heuristic - files that aren't imported and aren't main modules
        all_imports = set()
        for imports in self.analysis['imports'].values():
            all_imports.update(imports)
        
        for file_path in self.analysis['file_sizes'].keys():
            rel_path = str(Path(file_path).relative_to(self.src_path))
            module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Skip main modules and __init__ files
            if any(main in rel_path for main in ['main_app.py', '__init__.py', 'run_dashboard.py']):
                continue
            
            # Check if this module is imported anywhere
            is_imported = any(imp in all_imports for imp in [
                module_name, 
                module_name.split('.')[-1],  # Just the file name
                rel_path
            ])
            
            if not is_imported and file_path.endswith('.py'):
                self.analysis['unused_files'].append(rel_path)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        logger.info("📊 Generating analysis report...")
        
        # Summary statistics
        total_size = sum(self.analysis['file_sizes'].values())
        avg_size = total_size / max(self.analysis['total_files'], 1)
        
        report = {
            'summary': {
                'total_files': self.analysis['total_files'],
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'average_file_size': round(avg_size, 0)
            },
            'file_categories': {
                'backup_files': len(self.analysis['backup_files']),
                'test_files': len(self.analysis['test_files']),
                'config_files': len(self.analysis['config_files']),
                'service_files': len(self.analysis['service_files']),
                'route_files': len(self.analysis['route_files']),
                'main_modules': len(self.analysis['main_modules'])
            },
            'code_metrics': {
                'total_functions': sum(len(funcs) for funcs in self.analysis['functions'].values()),
                'total_classes': sum(len(classes) for classes in self.analysis['classes'].values()),
                'unique_imports': len(set().union(*self.analysis['imports'].values()))
            },
            'potential_issues': {
                'backup_files_count': len(self.analysis['backup_files']),
                'potential_duplicates': len(self.analysis['potential_duplicates']),
                'potentially_unused': len(self.analysis['unused_files'])
            },
            'detailed_analysis': {
                'backup_files': self.analysis['backup_files'],
                'potential_duplicates': self.analysis['potential_duplicates'][:10],  # Top 10
                'potentially_unused': self.analysis['unused_files'][:20],  # Top 20
                'largest_files': sorted(
                    [(path, size) for path, size in self.analysis['file_sizes'].items()],
                    key=lambda x: x[1], reverse=True
                )[:10]
            }
        }
        
        return report
    
    def run_analysis(self) -> Dict:
        """Run complete analysis"""
        logger.info("🚀 Starting codebase analysis...")
        
        if not self.src_path.exists():
            logger.error(f"❌ Source path {self.src_path} does not exist")
            return {}
        
        self.analyze_file_structure()
        self.analyze_imports_and_functions()
        self.find_potential_duplicates()
        self.identify_unused_files()
        
        report = self.generate_report()
        
        logger.info("✅ Analysis complete")
        return report

def create_cleanup_plan(report: Dict) -> Dict:
    """Create a SAFE cleanup plan based on analysis"""
    
    cleanup_plan = {
        'safe_to_remove': [],
        'needs_review': [],
        'keep_files': [],
        'recommendations': []
    }
    
    # Safe to remove: obvious backup files
    for backup_file in report['detailed_analysis']['backup_files']:
        if any(suffix in backup_file.lower() for suffix in ['_backup.py', '_old.py', '_clean.py', '_fixed.py']):
            cleanup_plan['safe_to_remove'].append({
                'file': backup_file,
                'reason': 'Backup file with obvious suffix'
            })
    
    # Needs review: potential duplicates
    for duplicate in report['detailed_analysis']['potential_duplicates']:
        cleanup_plan['needs_review'].append({
            'files': duplicate['files'],
            'reason': f"Potential duplicate function: {duplicate['function']}"
        })
    
    # Keep files: main modules and configs
    keep_patterns = ['main_app.py', '__init__.py', 'config/', 'monitoring/']
    for file_path in report['detailed_analysis']['largest_files']:
        if any(pattern in file_path[0] for pattern in keep_patterns):
            cleanup_plan['keep_files'].append({
                'file': file_path[0],
                'reason': 'Core application file'
            })
    
    # Recommendations
    if report['potential_issues']['backup_files_count'] > 5:
        cleanup_plan['recommendations'].append("Consider removing backup files to reduce codebase size")
    
    if report['potential_issues']['potential_duplicates'] > 3:
        cleanup_plan['recommendations'].append("Review duplicate functions for consolidation opportunities")
    
    if report['summary']['total_files'] > 50:
        cleanup_plan['recommendations'].append("Large codebase - consider organizing into more focused modules")
    
    return cleanup_plan

def main():
    """Main analysis function"""
    print("🏋️ Safe Codebase Analysis")
    print("=========================")
    
    analyzer = SafeCodebaseAnalyzer("src")
    report = analyzer.run_analysis()
    
    if not report:
        print("❌ Analysis failed")
        return False
    
    # Display summary
    print(f"\n📊 Codebase Summary:")
    print(f"  • Total files: {report['summary']['total_files']}")
    print(f"  • Total size: {report['summary']['total_size_mb']} MB")
    print(f"  • Functions: {report['code_metrics']['total_functions']}")
    print(f"  • Classes: {report['code_metrics']['total_classes']}")
    
    print(f"\n🗂️ File Categories:")
    for category, count in report['file_categories'].items():
        print(f"  • {category}: {count}")
    
    print(f"\n⚠️ Potential Issues:")
    for issue, count in report['potential_issues'].items():
        print(f"  • {issue}: {count}")
    
    if report['detailed_analysis']['backup_files']:
        print(f"\n📁 Backup Files Found:")
        for backup_file in report['detailed_analysis']['backup_files'][:10]:
            print(f"  • {backup_file}")
        if len(report['detailed_analysis']['backup_files']) > 10:
            print(f"  ... and {len(report['detailed_analysis']['backup_files']) - 10} more")
    
    # Create cleanup plan
    cleanup_plan = create_cleanup_plan(report)
    
    print(f"\n🧹 Safe Cleanup Plan:")
    print(f"  • Safe to remove: {len(cleanup_plan['safe_to_remove'])} files")
    print(f"  • Needs review: {len(cleanup_plan['needs_review'])} items")
    print(f"  • Keep files: {len(cleanup_plan['keep_files'])} files")
    
    if cleanup_plan['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in cleanup_plan['recommendations']:
            print(f"  • {rec}")
    
    # Save detailed reports
    try:
        with open('codebase_analysis.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n✅ Detailed analysis saved to: codebase_analysis.json")
        
        with open('cleanup_plan.json', 'w') as f:
            json.dump(cleanup_plan, f, indent=2, default=str)
        print(f"✅ Cleanup plan saved to: cleanup_plan.json")
        
    except Exception as e:
        print(f"⚠️ Could not save report files: {e}")
    
    print(f"\n🎉 Analysis complete! Review the files before any cleanup actions.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)