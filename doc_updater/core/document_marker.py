from typing import Dict, List, Any, Optional, Tuple
import os
import re

class RuleParser:
    def __init__(self):
        self.rules = []
        self.rule_content = ""

    def load_rule_from_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.rule_content = f.read()
            self._parse_rule_content()
            return True
        except Exception as e:
            print(f"加载规则文件失败: {e}")
            return False

    def load_rule_from_text(self, rule_text: str):
        self.rule_content = rule_text
        self._parse_rule_content()

    def _parse_rule_content(self):
        self.rules = []
        lines = self.rule_content.strip().split('\n')

        rule_text = ' '.join([line.strip() for line in lines if line.strip() and not line.strip().startswith('#')])

        if 'E列' in rule_text and '否' in rule_text and 'C列' in rule_text and 'Q列' in rule_text and 'NA' in rule_text:
            rule = {
                'type': 'input_column_e_equals_no_set_platform_q_to_na',
                'condition_column': 'E',
                'condition_value': '否',
                'source_id_column': 'C',
                'platform_id_column': 'Q',
                'action': 'set_q_to_na_copy_p_to_r',
                'new_q_value': 'NA'
            }
            self.rules.append(rule)

    def _parse_if_then_rule(self, line: str) -> Optional[Dict[str, Any]]:
        try:
            if_part, then_part = line.split('则', 1)

            condition = {}
            if 'E列' in if_part and '否' in if_part:
                condition['type'] = 'input_column_e_equals_no'
                id_match = if_part[if_part.find('C列'):].split()[1] if 'C列' in if_part else None
                condition['source_column'] = 'C'
                condition['condition_value'] = '否'
                condition['target_column'] = 'Q'

            if 'Q列' in then_part and 'ID号' in then_part:
                condition['action'] = 'set_q_to_na_copy_p_to_r'

            if condition.get('type') and condition.get('action'):
                return condition

        except Exception as e:
            print(f"解析规则失败: {e}")

        return None

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.rules

class DocumentMarker:
    def __init__(self):
        self.rule_parser = RuleParser()
        self.marking_results = []

    def load_rule(self, rule_source: str) -> bool:
        if os.path.isfile(rule_source):
            return self.rule_parser.load_rule_from_file(rule_source)
        else:
            self.rule_parser.load_rule_from_text(rule_source)
            return True

    def apply_marking_rules(self, input_data: List[List[Any]], platform_data: List[Dict[str, Any]], sheet_names: List[str]) -> Tuple[List[Dict[str, Any]], List[List[Any]]]:
        changes = []
        rules = self.rule_parser.get_rules()

        id_column_no_list = []

        for rule in rules:
            if rule.get('type') == 'input_column_e_equals_no_set_platform_q_to_na':
                id_column_no_list = self._extract_ids_from_input(input_data)

        if id_column_no_list:
            changes = self._apply_marking_to_platform(platform_data, id_column_no_list, sheet_names)

        self.marking_results = changes
        return changes, platform_data

    def _extract_ids_from_input(self, input_data: List[List[Any]]) -> List[str]:
        ids = []

        if len(input_data) < 2:
            return ids

        header_row = input_data[0] if input_data else []
        data_rows = input_data[1:] if len(input_data) > 1 else []

        col_c_index = -1
        col_e_index = -1

        for idx, header in enumerate(header_row):
            header_str = str(header).strip().upper()
            if header_str in ['C', 'C列', 'ID']:
                col_c_index = idx
            elif header_str in ['E', 'E列', '打点结果', '结果']:
                col_e_index = idx

        for row in data_rows:
            if col_e_index >= 0 and col_e_index < len(row):
                cell_value = str(row[col_e_index]).strip()
                if cell_value == '否':
                    if col_c_index >= 0 and col_c_index < len(row):
                        id_value = str(row[col_c_index]).strip()
                        if id_value:
                            ids.append(id_value)

        return ids

    def _apply_marking_to_platform(self, platform_data: List[Dict[str, Any]], id_list: List[str], sheet_names: List[str]) -> List[Dict[str, Any]]:
        changes = []

        for sheet_idx, sheet_info in enumerate(platform_data):
            sheet_name = sheet_info.get('sheet_name', f'Sheet{sheet_idx+1}')
            rows = sheet_info.get('rows', [])

            if len(rows) < 2:
                continue

            header_row = rows[0]
            data_rows = rows[1:]

            col_p_index = -1
            col_q_index = -1
            col_r_index = -1
            col_status_index = -1
            col_reason_index = -1

            for idx, header in enumerate(header_row):
                header_str = str(header).strip() if header else ''
                header_upper = header_str.upper()
                if '适用范围' in header_str:
                    col_p_index = idx
                elif 'STATUS' in header_upper and '供应商状态' in header_str:
                    col_q_index = idx
                elif 'COMMENTS' in header_upper and '供应商意见' in header_str:
                    col_r_index = idx
                elif '实现状态' in header_str and ('YES/NO' in header_upper or 'Yes/No' in header_str):
                    col_status_index = idx
                elif '不能实现的原因' in header_str:
                    col_reason_index = idx

            for row_idx, row in enumerate(data_rows):
                if col_p_index >= 0 and col_p_index < len(row):
                    p_value = str(row[col_p_index]).strip() if row[col_p_index] else ''

                    for id_value in id_list:
                        pattern = rf'(?:^|\s|\(|\[|,|;){re.escape(id_value)}(?:$|\s|\)|\]|,|;)'
                        if re.search(pattern, p_value):
                            original_q = row[col_q_index] if col_q_index >= 0 and col_q_index < len(row) else ''
                            original_p = p_value

                            original_status = ''
                            if col_status_index >= 0 and col_status_index < len(row):
                                original_status = str(row[col_status_index]).strip() if row[col_status_index] else ''

                            original_reason = ''
                            if col_reason_index >= 0 and col_reason_index < len(row):
                                original_reason = str(row[col_reason_index]).strip() if row[col_reason_index] else ''

                            if sheet_names and sheet_idx < len(sheet_names):
                                actual_sheet_name = sheet_names[sheet_idx]
                            else:
                                actual_sheet_name = sheet_name

                            changes.append({
                                'sheet_name': actual_sheet_name,
                                'row': row_idx + 2,
                                'column_q_original': original_q,
                                'column_p_value': original_p,
                                'column_q_new': 'NA',
                                'column_r_new': original_p if original_p else '',
                                'column_status_original': original_status,
                                'column_status_new': 'No',
                                'column_reason_original': original_reason,
                                'column_reason_new': original_p if original_p else ''
                            })
                            break

        return changes

    def get_marking_results(self) -> List[Dict[str, Any]]:
        return self.marking_results

    def get_changes_summary(self) -> str:
        if not self.marking_results:
            return "无打点变更"

        summary = f"共 {len(self.marking_results)} 项变更:\n"
        for change in self.marking_results:
            summary += f"Sheet: {change.get('sheet_name')}, 行: {change.get('row')}, "
            summary += f"Q列: {change.get('column_q_original')} -> {change.get('column_q_new')}, "
            summary += f"R列: {change.get('column_r_new')}\n"

        return summary
