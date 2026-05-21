from typing import List, Dict, Any, Optional
from config import Settings, ChangeType

class Updater:
    def __init__(self):
        self.updates = []
        self.conflicts = []

    def prepare_updates(self, mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.updates = []

        for mapping in mappings:
            confidence = mapping.get('confidence', 0)
            if confidence >= Settings.MATCH_THRESHOLD:
                self.updates.append({
                    'old_value': mapping.get('old_value', ''),
                    'new_value': mapping.get('new_value', ''),
                    'confidence': confidence,
                    'status': 'pending'
                })

        return self.updates

    def apply_updates(self, document_data: List[List[Any]], update_list: List[Dict[str, Any]]) -> tuple[List[List[Any]], List[Dict[str, Any]]]:
        updated_data = []
        applied_updates = []

        for row in document_data:
            new_row = []
            for cell in row:
                cell_str = str(cell) if cell is not None else ''
                updated = False

                for update in update_list:
                    if update['status'] == 'pending' and update['old_value'] == cell_str:
                        new_row.append(update['new_value'])
                        update['status'] = 'applied'
                        applied_updates.append(update)
                        updated = True
                        break

                if not updated:
                    new_row.append(cell)

            updated_data.append(new_row)

        return updated_data, applied_updates

    def update_xlsx(self, xlsx_handler, update_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        applied = []

        for update in update_list:
            old_value = update.get('old_value', '')
            new_value = update.get('new_value', '')

            matches = xlsx_handler.find_matching_cells(old_value)

            for sheet_idx, row_idx, col_idx, matched_value in matches:
                if xlsx_handler.update_cell(sheet_idx, row_idx, col_idx, old_value, new_value):
                    applied.append({
                        'old_value': old_value,
                        'new_value': new_value,
                        'location': f"Sheet{sheet_idx+1} Row{row_idx+1} Col{col_idx+1}",
                        'status': 'applied'
                    })

        return applied

    def update_docx(self, docx_handler, update_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        applied = []

        for update in update_list:
            old_value = update.get('old_value', '')
            new_value = update.get('new_value', '')

            count = docx_handler.replace_text(old_value, new_value)

            if count > 0:
                applied.append({
                    'old_value': old_value,
                    'new_value': new_value,
                    'location': f"{count}处",
                    'status': 'applied'
                })

        return applied

    def update_txt(self, txt_handler, update_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        applied = []

        for update in update_list:
            old_value = update.get('old_value', '')
            new_value = update.get('new_value', '')

            count = txt_handler.replace_text(old_value, new_value)

            if count > 0:
                applied.append({
                    'old_value': old_value,
                    'new_value': new_value,
                    'location': f"{count}处",
                    'status': 'applied'
                })

        return applied

    def detect_conflicts(self, old_value: str, new_value: str, existing_updates: List[Dict[str, Any]]) -> bool:
        for update in existing_updates:
            if update.get('old_value') == old_value and update.get('new_value') != new_value:
                self.conflicts.append({
                    'old_value': old_value,
                    'conflicting_updates': [update.get('new_value'), new_value]
                })
                return True
        return False

    def get_pending_updates(self) -> List[Dict[str, Any]]:
        return [u for u in self.updates if u.get('status') == 'pending']

    def get_applied_updates(self) -> List[Dict[str, Any]]:
        return [u for u in self.updates if u.get('status') == 'applied']

    def get_conflicts(self) -> List[Dict[str, Any]]:
        return self.conflicts

    def clear_updates(self):
        self.updates = []
        self.conflicts = []
