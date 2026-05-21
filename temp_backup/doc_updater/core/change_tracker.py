from typing import List, Dict, Any
from datetime import datetime
from config import ChangeType

class ChangeTracker:
    def __init__(self):
        self.changes = []
        self.change_history = []

    def record_change(self, change_type: str, old_value: Any, new_value: Any, location: str) -> None:
        change_record = {
            'type': change_type,
            'old_value': str(old_value) if old_value is not None else '',
            'new_value': str(new_value) if new_value is not None else '',
            'location': location,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'completed'
        }

        self.changes.append(change_record)
        self.change_history.append(change_record)

    def record_addition(self, value: Any, location: str) -> None:
        self.record_change(ChangeType.ADD, '', value, location)

    def record_modification(self, old_value: Any, new_value: Any, location: str) -> None:
        self.record_change(ChangeType.MODIFY, old_value, new_value, location)

    def record_deletion(self, value: Any, location: str) -> None:
        self.record_change(ChangeType.DELETE, value, '', location)

    def get_changes(self) -> List[Dict[str, Any]]:
        return self.changes

    def get_change_summary(self) -> Dict[str, int]:
        summary = {
            'add': 0,
            'modify': 0,
            'delete': 0,
            'total': len(self.changes)
        }

        for change in self.changes:
            change_type = change.get('type', 'none')
            if change_type in summary:
                summary[change_type] += 1

        return summary

    def get_changes_by_type(self, change_type: str) -> List[Dict[str, Any]]:
        return [c for c in self.changes if c.get('type') == change_type]

    def clear_changes(self) -> None:
        self.changes = []

    def export_changes(self, format: str = 'excel') -> List[Dict[str, Any]]:
        if format == 'excel':
            return self.changes
        elif format == 'json':
            return self.changes
        elif format == 'txt':
            return self.changes
        return self.changes

    def get_change_report(self) -> str:
        summary = self.get_change_summary()

        report_lines = [
            "=" * 60,
            "文档变更报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"变更总数: {summary['total']}",
            "-" * 60,
            f"新增: {summary['add']} 项",
            f"修改: {summary['modify']} 项",
            f"删除: {summary['delete']} 项",
            "-" * 60,
            "详细变更记录:",
            "-" * 60
        ]

        for idx, change in enumerate(self.changes, 1):
            report_lines.append(f"\n[{idx}] {change.get('type', '').upper()}")
            report_lines.append(f"  位置: {change.get('location', '')}")
            report_lines.append(f"  原内容: {change.get('old_value', '')}")
            report_lines.append(f"  新内容: {change.get('new_value', '')}")
            report_lines.append(f"  时间: {change.get('timestamp', '')}")

        report_lines.append("=" * 60)

        return '\n'.join(report_lines)

    def validate_changes(self) -> Dict[str, Any]:
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        for idx, change in enumerate(self.changes):
            if not change.get('location'):
                validation_results['valid'] = False
                validation_results['errors'].append(f"变更 {idx+1}: 缺少位置信息")

            if change.get('type') == ChangeType.MODIFY:
                if not change.get('old_value') or not change.get('new_value'):
                    validation_results['warnings'].append(f"变更 {idx+1}: 修改操作缺少新旧值")

            if change.get('type') == ChangeType.ADD:
                if not change.get('new_value'):
                    validation_results['warnings'].append(f"变更 {idx+1}: 新增操作缺少新值")

            if change.get('type') == ChangeType.DELETE:
                if not change.get('old_value'):
                    validation_results['warnings'].append(f"变更 {idx+1}: 删除操作缺少原值")

        return validation_results
