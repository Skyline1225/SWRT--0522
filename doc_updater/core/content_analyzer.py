from typing import Dict, List, Any, Tuple
import re
from collections import Counter
import pandas as pd

class ContentAnalyzer:
    def __init__(self):
        self.keywords = []
        self.content_items = []

    def analyze(self, data: List[List[Any]]) -> Dict[str, Any]:
        self.content_items = self._flatten_data(data)
        keywords = self._extract_keywords(self.content_items)
        changes = self._identify_changes(self.content_items)

        return {
            'keywords': keywords,
            'items': self.content_items,
            'changes': changes,
            'total_items': len(self.content_items),
            'statistics': self._calculate_statistics()
        }

    def _flatten_data(self, data: List[List[Any]]) -> List[str]:
        items = []
        for row in data:
            for cell in row:
                if cell and str(cell).strip():
                    items.append(str(cell).strip())
        return items

    def _extract_keywords(self, items: List[str], top_n: int = 50) -> List[str]:
        all_words = []
        for item in items:
            words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', str(item))
            all_words.extend([w for w in words if len(w) >= 2])

        word_freq = Counter(all_words)
        keywords = [word for word, freq in word_freq.most_common(top_n)]
        self.keywords = keywords
        return keywords

    def _identify_changes(self, items: List[str]) -> List[Dict[str, Any]]:
        changes = []
        for idx, item in enumerate(items):
            change_type = self._detect_change_type(item)
            if change_type != 'none':
                changes.append({
                    'index': idx,
                    'content': item,
                    'type': change_type,
                    'keywords': self._extract_item_keywords(item)
                })
        return changes

    def _detect_change_type(self, item: str) -> str:
        item_lower = item.lower()
        if any(marker in item_lower for marker in ['新增', 'add', '新建', '+']):
            return 'add'
        elif any(marker in item_lower for marker in ['修改', 'update', '变更', '改']):
            return 'modify'
        elif any(marker in item_lower for marker in ['删除', 'delete', '移除', '-']):
            return 'delete'
        return 'none'

    def _extract_item_keywords(self, item: str) -> List[str]:
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', str(item))
        return [w for w in words if len(w) >= 2]

    def _calculate_statistics(self) -> Dict[str, Any]:
        total = len(self.content_items)
        unique = len(set(self.content_items))

        return {
            'total_items': total,
            'unique_items': unique,
            'duplicate_count': total - unique
        }

    def compare_documents(self, input_data: List[List[Any]], platform_data: List[List[Any]]) -> List[Dict[str, Any]]:
        input_flat = self._flatten_data(input_data)
        platform_flat = self._flatten_data(platform_data)

        input_set = set(input_flat)
        platform_set = set(platform_flat)

        additions = input_set - platform_set
        deletions = platform_set - input_set
        common = input_set & platform_set

        comparison_results = []

        for item in additions:
            comparison_results.append({
                'content': item,
                'type': 'add',
                'similar_items': self._find_similar_items(item, platform_flat)
            })

        for item in deletions:
            comparison_results.append({
                'content': item,
                'type': 'delete',
                'similar_items': self._find_similar_items(item, input_flat)
            })

        return comparison_results

    def _find_similar_items(self, item: str, reference_list: List[str], threshold: float = 0.6) -> List[str]:
        similar = []
        item_keywords = set(self._extract_item_keywords(item))

        for ref_item in reference_list:
            ref_keywords = set(self._extract_item_keywords(ref_item))
            if item_keywords & ref_keywords:
                similarity = len(item_keywords & ref_keywords) / len(item_keywords | ref_keywords)
                if similarity >= threshold:
                    similar.append(ref_item)

        return similar[:5]

    def get_update_mapping(self, input_data: List[List[Any]], platform_data: List[List[Any]]) -> List[Dict[str, Any]]:
        mappings = []
        comparison = self.compare_documents(input_data, platform_data)

        for comp in comparison:
            if comp['type'] == 'add' and comp['similar_items']:
                for similar in comp['similar_items']:
                    mappings.append({
                        'old_value': similar,
                        'new_value': comp['content'],
                        'confidence': self._calculate_similarity(comp['content'], similar)
                    })

        return sorted(mappings, key=lambda x: x['confidence'], reverse=True)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        words1 = set(self._extract_item_keywords(str1))
        words2 = set(self._extract_item_keywords(str2))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0
