from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QTableWidget,
                             QTableWidgetItem, QGroupBox, QSplitter, QTextEdit,
                             QProgressBar, QStatusBar, QMessageBox, QMenuBar,
                             QMenu, QAction, QTabWidget, QFrame, QApplication,
                             QDialog, QDialogButtonBox, QSizePolicy, QComboBox,
                             QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
import os
import sys
import traceback


class ErrorDisplayDialog(QDialog):
    """错误信息显示对话框"""
    def __init__(self, errors, title="文档检查错误", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.errors = errors
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel(f"共发现 {len(self.errors)} 个错误，请修正后重试：")
        info_font = QFont()
        info_font.setPointSize(11)
        info_label.setFont(info_font)
        layout.addWidget(info_label)

        error_text = QTextEdit()
        error_text.setReadOnly(True)

        content = ""
        for i, error in enumerate(self.errors, 1):
            content += f"{i}. {str(error)}\n"

        error_text.setText(content)
        layout.addWidget(error_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class ExportDialog(QDialog):
    """文档导出对话框"""
    def __init__(self, title, has_changes=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 200)
        self.has_changes = has_changes
        self.export_changes = False
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        file_label = QLabel('导出路径:')
        self.file_edit = QLabel('未选择')
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        if self.has_changes:
            self.export_changes_check = QCheckBox('同时导出变更履历')
            self.export_changes_check.setChecked(True)
            layout.addWidget(self.export_changes_check)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def browse_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '选择导出路径', '', 
                                                   'Excel工作簿 (*.xlsx);;Word文档 (*.docx);;PDF文档 (*.pdf);;文本文件 (*.txt)')
        if file_path:
            self.file_path = file_path
            self.file_edit.setText(os.path.basename(file_path))

    def get_export_settings(self):
        return {
            'file_path': self.file_path,
            'export_changes': self.export_changes_check.isChecked() if self.has_changes else False
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.platform_file = None
        self.output_file = None
        self.changes = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SWRT文档内容更新软件')

        screen = QApplication.primaryScreen().availableGeometry() if QApplication.primaryScreen() else None
        target_width = 1200
        target_height = 800
        if screen:
            target_width = min(target_width, int(screen.width() * 0.95))
            target_height = min(target_height, int(screen.height() * 0.9))
        self.resize(target_width, target_height)
        if screen:
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2,
            )

        self.setup_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        header = self.create_header()
        main_layout.addWidget(header)

        content_splitter = self.create_content_area()
        main_layout.addWidget(content_splitter, 1)

        footer = self.create_footer()
        main_layout.addWidget(footer)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('就绪')

        self.load_stylesheet()

    def setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件')

        import_input_action = QAction('导入SWRT输入文档', self)
        import_input_action.triggered.connect(lambda: self.import_file('input'))
        file_menu.addAction(import_input_action)

        import_platform_action = QAction('导入SWRT平台文档', self)
        import_platform_action.triggered.connect(lambda: self.import_file('platform'))
        file_menu.addAction(import_platform_action)

        show_rules_action = QAction('显示打点规则', self)
        show_rules_action.triggered.connect(self.show_marking_rules)
        file_menu.addAction(show_rules_action)

        file_menu.addSeparator()

        check_input_action = QAction('检查SWRT输入文档', self)
        check_input_action.triggered.connect(lambda: self.check_document('input'))
        file_menu.addAction(check_input_action)

        check_platform_action = QAction('检查SWRT平台文档', self)
        check_platform_action.triggered.connect(lambda: self.check_document('platform'))
        file_menu.addAction(check_platform_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu('文档导出')

        export_input_action = QAction('导出SWRT输入文档', self)
        export_input_action.triggered.connect(lambda: self.export_document('input'))
        export_menu.addAction(export_input_action)

        export_platform_action = QAction('导出SWRT平台文档', self)
        export_platform_action.triggered.connect(lambda: self.export_document('platform'))
        export_menu.addAction(export_platform_action)

        export_updated_action = QAction('导出更新后文档', self)
        export_updated_action.triggered.connect(lambda: self.export_document('updated'))
        export_menu.addAction(export_updated_action)

        file_menu.addSeparator()

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu('帮助')

        help_action = QAction('帮助', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_header(self):
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel('SWRT文档内容更新软件')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.mark_btn = QPushButton('执行打点')
        self.mark_btn.clicked.connect(self.execute_marking)
        self.mark_btn.setEnabled(False)

        header_layout.addWidget(self.mark_btn)

        return header_frame

    def create_content_area(self):
        splitter = QSplitter(Qt.Horizontal)

        left_panel = self.create_file_panel()
        splitter.addWidget(left_panel)

        center_panel = self.create_preview_panel()
        splitter.addWidget(center_panel)

        right_panel = self.create_info_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 600, 200])

        return splitter

    def create_file_panel(self):
        group = QGroupBox('文件导入')

        layout = QVBoxLayout(group)

        input_group = QGroupBox('SWRT输入文档')
        input_layout = QVBoxLayout()

        self.input_label = QLabel('未导入文件')
        self.input_label.setWordWrap(True)
        input_layout.addWidget(self.input_label)

        input_btn_layout = QHBoxLayout()
        import_input_btn = QPushButton('导入')
        import_input_btn.clicked.connect(lambda: self.import_file('input'))

        check_input_btn = QPushButton('检查')
        check_input_btn.clicked.connect(lambda: self.check_document('input'))

        input_btn_layout.addWidget(import_input_btn)
        input_btn_layout.addWidget(check_input_btn)
        input_btn_layout.addStretch()
        input_layout.addLayout(input_btn_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        platform_group = QGroupBox('SWRT平台文档')
        platform_layout = QVBoxLayout()

        self.platform_label = QLabel('未导入文件')
        self.platform_label.setWordWrap(True)
        platform_layout.addWidget(self.platform_label)

        platform_btn_layout = QHBoxLayout()
        import_platform_btn = QPushButton('导入')
        import_platform_btn.clicked.connect(lambda: self.import_file('platform'))

        check_platform_btn = QPushButton('检查')
        check_platform_btn.clicked.connect(lambda: self.check_document('platform'))

        platform_btn_layout.addWidget(import_platform_btn)
        platform_btn_layout.addWidget(check_platform_btn)
        platform_btn_layout.addStretch()
        platform_layout.addLayout(platform_btn_layout)

        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)

        layout.addStretch()

        return group

    def create_preview_panel(self):
        group = QGroupBox('文档预览')

        layout = QVBoxLayout(group)

        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setElideMode(Qt.ElideNone)
        self.tab_widget.tabBar().setUsesScrollButtons(True)
        self.tab_widget.tabBar().setExpanding(False)

        input_preview_widget = QWidget()
        input_preview_layout = QVBoxLayout(input_preview_widget)

        input_sheet_layout = QHBoxLayout()
        input_sheet_layout.addWidget(QLabel('工作表:'))
        self.input_sheet_combo = QComboBox()
        self.input_sheet_combo.currentIndexChanged.connect(lambda: self.on_input_sheet_changed())
        input_sheet_layout.addWidget(self.input_sheet_combo)
        input_sheet_layout.addStretch()
        input_preview_layout.addLayout(input_sheet_layout)

        self.input_preview = QTableWidget()
        input_preview_layout.addWidget(self.input_preview)

        self.tab_widget.addTab(input_preview_widget, 'SWRT输入文档预览')

        platform_preview_widget = QWidget()
        platform_preview_layout = QVBoxLayout(platform_preview_widget)

        platform_sheet_layout = QHBoxLayout()
        platform_sheet_layout.addWidget(QLabel('工作表:'))
        self.platform_sheet_combo = QComboBox()
        self.platform_sheet_combo.currentIndexChanged.connect(lambda: self.on_platform_sheet_changed())
        platform_sheet_layout.addWidget(self.platform_sheet_combo)
        platform_sheet_layout.addStretch()
        platform_preview_layout.addLayout(platform_sheet_layout)

        self.platform_preview = QTableWidget()
        platform_preview_layout.addWidget(self.platform_preview)

        self.tab_widget.addTab(platform_preview_widget, 'SWRT平台文档预览')

        self.changes_preview = QTableWidget()
        self.tab_widget.addTab(self.changes_preview, '变更预览')

        layout.addWidget(self.tab_widget)

        return group

    def create_info_panel(self):
        group = QGroupBox('信息面板')

        layout = QVBoxLayout(group)

        rules_group = QGroupBox('打点规则摘要')
        rules_layout = QVBoxLayout()

        rules_summary = QLabel('1. SWRT输入文档“打点结果”列="否"时提取“ID”列ID内容\n2. 在SWRT平台文档“适用范围”列匹配ID\n3. “供应商状态”列设为NA，“适用范围”列内容复制到“供应商意见”列\n4. "实现状态"列设为"No"\n5. "不能实现的原因"列设为P列内容')
        rules_summary.setWordWrap(True)
        rules_layout.addWidget(rules_summary)

        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)

        layout.addStretch()

        stats_group = QGroupBox('统计信息')
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel('暂无数据')
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

        return group

    def create_footer(self):
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.StyledPanel)
        footer_layout = QHBoxLayout(footer_frame)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        footer_layout.addWidget(self.progress_bar)

        return footer_frame

    def load_stylesheet(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)

            style_path = os.path.join(base_path, 'styles', 'main.qss')
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"加载样式表失败: {e}")

    def check_document(self, doc_type: str):
        """检查文档完整性"""
        try:
            from core import DocumentChecker

            checker = DocumentChecker()
            file_path = None
            title = ""

            if doc_type == 'input':
                if not self.input_file:
                    QMessageBox.warning(self, '提示', '请先导入SWRT输入文档')
                    return
                file_path = self.input_file
                title = "SWRT输入文档检查"
                passed, errors = checker.check_input_document(file_path)
            else:
                if not self.platform_file:
                    QMessageBox.warning(self, '提示', '请先导入SWRT平台文档')
                    return
                file_path = self.platform_file
                title = "SWRT平台文档检查"
                passed, errors = checker.check_platform_document(file_path)

            if passed:
                QMessageBox.information(self, title, f"文档检查通过，未发现错误！")
                self.status_bar.showMessage(f"{title} - 通过")
            else:
                dialog = ErrorDisplayDialog(errors, title, self)
                dialog.exec_()
                self.status_bar.showMessage(f"{title} - 发现 {len(errors)} 个错误")

        except Exception as e:
            QMessageBox.warning(self, '错误', f'文档检查失败:\n{str(e)}')
            traceback.print_exc()

    def import_file(self, file_type: str):
        filters = "支持的文件 (*.docx *.xlsx *.xls *.pdf *.txt);;Word文档 (*.docx);;Excel工作簿 (*.xlsx *.xls);;PDF文档 (*.pdf);;文本文件 (*.txt)"

        file_path, _ = QFileDialog.getOpenFileName(self, f'导入{"SWRT输入" if file_type == "input" else "SWRT平台"}文档', '', filters)

        if file_path:
            try:
                if file_type == 'input':
                    self.input_file = file_path
                    self.input_label.setText(os.path.basename(file_path))
                    self.load_preview(file_path, self.input_preview, self.input_sheet_combo)
                else:
                    self.platform_file = file_path
                    self.platform_label.setText(os.path.basename(file_path))
                    self.load_preview(file_path, self.platform_preview, self.platform_sheet_combo)

                self.status_bar.showMessage(f'已导入: {os.path.basename(file_path)}')

                if self.input_file and self.platform_file:
                    self.mark_btn.setEnabled(True)

            except Exception as e:
                QMessageBox.warning(self, '错误', f'导入文件失败:\n{str(e)}')
                traceback.print_exc()

    def execute_marking(self):
        if not self.input_file or not self.platform_file:
            QMessageBox.warning(self, '警告', '请先导入SWRT输入文档和SWRT平台文档')
            return

        try:
            from core import DocumentChecker
            checker = DocumentChecker()

            input_passed, input_errors = checker.check_input_document(self.input_file)
            if not input_passed:
                dialog = ErrorDisplayDialog(input_errors, "SWRT输入文档错误", self)
                dialog.exec_()
                return

            platform_passed, platform_errors = checker.check_platform_document(self.platform_file)
            if not platform_passed:
                dialog = ErrorDisplayDialog(platform_errors, "SWRT平台文档错误", self)
                dialog.exec_()
                return

        except Exception as e:
            reply = QMessageBox.question(
                self,
                '检查失败',
                f'文档完整性检查失败：{str(e)}\n\n是否继续执行打点？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        reply = QMessageBox.question(self, '确认', '确定要执行打点操作吗？',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                from formats import XlsxHandler
                from core import DocumentMarker
                import shutil
                import datetime

                self.status_bar.showMessage('正在执行打点...')
                self.progress_bar.setValue(20)

                input_handler = XlsxHandler()
                if not input_handler.read(self.input_file):
                    raise Exception("无法读取SWRT输入文档")

                self.progress_bar.setValue(40)

                ext = os.path.splitext(self.platform_file)[1].lower()
                if ext not in ['.xlsx', '.xls']:
                    raise Exception("SWRT平台文档必须是Excel文件")

                output_name = f"{os.path.splitext(os.path.basename(self.platform_file))[0]}_打点后{ext}"
                output_path = os.path.join(os.path.dirname(self.platform_file), output_name)
                shutil.copy2(self.platform_file, output_path)

                platform_handler = XlsxHandler()
                platform_handler.read(output_path)

                self.progress_bar.setValue(60)

                marker = DocumentMarker()
                
                built_in_rule = """1. 如果SWRT输入文档E列中的打点结果项为"否"，提取该列对应行的C列ID号
2. 识别SWRT平台文档中P列"适用范围"列的内容，如果包含上一步骤提取的ID号相同的内容，则把该行Q列的内容改为NA，并把P列的内容复制到R列中
3. 同时把"实现状态（Yes/No）"列的内容改为"No"
4. 把"不能实现的原因"列的内容设为P列的内容"""
                marker.load_rule(built_in_rule)

                changes, _ = marker.apply_marking_rules(
                    input_handler.get_all_values(),
                    platform_handler.data,
                    platform_handler.sheet_names
                )

                self.progress_bar.setValue(80)

                applied = platform_handler.apply_marking_changes(changes)
                platform_handler.save(output_path)

                self.progress_bar.setValue(100)
                self.output_file = output_path

                self.changes = []
                for change in applied:
                    self.changes.append({
                        'type': '修改',
                        'sheet_name': change.get('sheet_name', ''),
                        'row': change.get('row', 0),
                        'old_value': change.get('column_q_original', ''),
                        'new_value': change.get('column_q_new', ''),
                        'p_column_value': change.get('column_p_value', ''),
                        'r_column_new': change.get('column_r_new', ''),
                        'column_status_original': change.get('column_status_original', ''),
                        'column_status_new': change.get('column_status_new', ''),
                        'column_reason_original': change.get('column_reason_original', ''),
                        'column_reason_new': change.get('column_reason_new', ''),
                        'change_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                self.stats_label.setText(f"打点完成\nSWRT输入文档: {os.path.basename(self.input_file)}\nSWRT平台文档: {os.path.basename(self.platform_file)}\n变更数量: {len(applied)} 项")

                self.display_changes()

                QMessageBox.information(self, '成功', f'打点完成!\n已处理 {len(applied)} 项变更\n保存至:\n{output_path}')
                self.status_bar.showMessage(f'打点完成: {os.path.basename(output_path)}')

            except Exception as e:
                QMessageBox.warning(self, '错误', f'打点失败:\n{str(e)}')
                traceback.print_exc()
                self.progress_bar.setValue(0)

    def load_preview(self, file_path, table_widget, sheet_combo):
        try:
            from formats import XlsxHandler, DocxHandler, PdfHandler, TxtHandler
            from utils import get_file_extension

            ext = get_file_extension(file_path)

            if ext in ['xlsx', 'xls']:
                handler = XlsxHandler()
                if handler.read(file_path):
                    sheet_combo.blockSignals(True)
                    sheet_combo.clear()
                    for sheet_name in handler.sheet_names:
                        sheet_combo.addItem(sheet_name)
                    sheet_combo.blockSignals(False)

                    if 'input' in file_path.lower() or file_path == getattr(self, 'input_file', None):
                        self.input_preview_handler = handler
                    else:
                        self.platform_preview_handler = handler

                    self.update_preview_table_for_handler(handler, table_widget, 0)
                    return
            elif ext == 'docx':
                handler = DocxHandler()
                if handler.read(file_path):
                    data = [[p['text']] for p in handler.get_paragraphs()]
                    self.populate_table(table_widget, data)
            elif ext == 'pdf':
                handler = PdfHandler()
                if handler.read(file_path):
                    data = [[line] for line in handler.get_all_text().split('\n') if line.strip()]
                    self.populate_table(table_widget, data)
            elif ext == 'txt':
                handler = TxtHandler()
                if handler.read(file_path):
                    data = [[line] for line in handler.get_lines()]
                    self.populate_table(table_widget, data)

        except Exception as e:
            print(f"预览加载失败: {e}")
            traceback.print_exc()

    def update_preview_table_for_handler(self, handler, table_widget, sheet_index):
        if not handler or sheet_index >= len(handler.data):
            return

        sheet_data = handler.data[sheet_index]
        rows = sheet_data.get('rows', [])

        table_widget.clear()
        if not rows:
            table_widget.setRowCount(0)
            table_widget.setColumnCount(0)
            return

        max_cols = max(len(row) for row in rows) if rows else 1
        table_widget.setRowCount(min(len(rows), 1000))
        table_widget.setColumnCount(max_cols)

        for row_idx, row_data in enumerate(rows[:1000]):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value) if cell_value is not None else '')
                table_widget.setItem(row_idx, col_idx, item)

        table_widget.resizeColumnsToContents()

    def on_input_sheet_changed(self):
        if hasattr(self, 'input_preview_handler'):
            index = self.input_sheet_combo.currentIndex()
            self.update_preview_table_for_handler(self.input_preview_handler, self.input_preview, index)

    def on_platform_sheet_changed(self):
        if hasattr(self, 'platform_preview_handler'):
            index = self.platform_sheet_combo.currentIndex()
            self.update_preview_table_for_handler(self.platform_preview_handler, self.platform_preview, index)

    def update_preview_table(self, table_widget, sheet_index):
        if not hasattr(self, 'preview_handler') or not self.preview_handler:
            return

        handler = self.preview_handler
        if sheet_index >= len(handler.data):
            return

        sheet_data = handler.data[sheet_index]
        rows = sheet_data.get('rows', [])

        table_widget.clear()
        if not rows:
            table_widget.setRowCount(0)
            table_widget.setColumnCount(0)
            return

        max_cols = max(len(row) for row in rows) if rows else 1
        table_widget.setRowCount(min(len(rows), 1000))
        table_widget.setColumnCount(max_cols)

        for row_idx, row_data in enumerate(rows[:1000]):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value) if cell_value is not None else '')
                table_widget.setItem(row_idx, col_idx, item)

        table_widget.resizeColumnsToContents()

    def populate_table(self, table_widget, data):
        table_widget.clear()
        table_widget.setRowCount(min(len(data), 1000))
        table_widget.setColumnCount(max(len(row) if data else 1, 1))

        for row_idx, row_data in enumerate(data[:1000]):
            for col_idx, cell_value in enumerate(row_data):
                item = QTableWidgetItem(str(cell_value) if cell_value else '')
                table_widget.setItem(row_idx, col_idx, item)

        table_widget.resizeColumnsToContents()

    def display_changes(self):
        self.changes_preview.clear()
        self.changes_preview.setRowCount(len(self.changes))
        self.changes_preview.setColumnCount(11)

        headers = ['变更时间', '工作表', '行号', '变更类型', 'Q列原值', 'Q列新值', 'R列新值', '实现状态原值', '实现状态新值', '不能实现的原因原值', '不能实现的原因新值']
        self.changes_preview.setHorizontalHeaderLabels(headers)

        for row_idx, change in enumerate(self.changes):
            self.changes_preview.setItem(row_idx, 0, QTableWidgetItem(change.get('change_time', '')))
            self.changes_preview.setItem(row_idx, 1, QTableWidgetItem(change.get('sheet_name', '')))
            self.changes_preview.setItem(row_idx, 2, QTableWidgetItem(str(change.get('row', 0))))
            self.changes_preview.setItem(row_idx, 3, QTableWidgetItem(change.get('type', '')))
            self.changes_preview.setItem(row_idx, 4, QTableWidgetItem(str(change.get('old_value', ''))))
            self.changes_preview.setItem(row_idx, 5, QTableWidgetItem(str(change.get('new_value', ''))))
            self.changes_preview.setItem(row_idx, 6, QTableWidgetItem(str(change.get('r_column_new', ''))))
            self.changes_preview.setItem(row_idx, 7, QTableWidgetItem(str(change.get('column_status_original', ''))))
            self.changes_preview.setItem(row_idx, 8, QTableWidgetItem(str(change.get('column_status_new', ''))))
            self.changes_preview.setItem(row_idx, 9, QTableWidgetItem(str(change.get('column_reason_original', ''))))
            self.changes_preview.setItem(row_idx, 10, QTableWidgetItem(str(change.get('column_reason_new', ''))))

        self.changes_preview.resizeColumnsToContents()

    def export_document(self, doc_type='updated'):
        source_file = None
        title = ''

        if doc_type == 'input':
            source_file = self.input_file
            title = 'SWRT输入文档'
        elif doc_type == 'platform':
            source_file = self.platform_file
            title = 'SWRT平台文档'
        elif doc_type == 'updated':
            source_file = self.output_file
            title = '更新后文档'

        if not source_file:
            QMessageBox.warning(self, '警告', f'没有可导出的{title}')
            return

        has_changes = doc_type == 'updated' and len(self.changes) > 0
        dialog = ExportDialog(f'导出{title}', has_changes, self)
        
        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_export_settings()
            file_path = settings['file_path']
            export_changes = settings.get('export_changes', False)

            if not file_path:
                QMessageBox.warning(self, '警告', '请选择导出路径')
                return

            try:
                import shutil
                shutil.copy2(source_file, file_path)

                if export_changes and self.changes:
                    self._export_changes_to_document(file_path)

                QMessageBox.information(self, '成功', f'{title}已导出至:\n{file_path}')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导出失败:\n{str(e)}')

    def _export_changes_to_document(self, file_path):
        """将变更履历追加到导出的文档中"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.xlsx', '.xls']:
                from formats import XlsxHandler
                handler = XlsxHandler()
                if handler.read(file_path):
                    self._add_changes_sheet(handler)
                    handler.save(file_path)
            elif ext == '.txt':
                self._append_changes_to_txt(file_path)
                
        except Exception as e:
            print(f"导出变更履历失败: {e}")
            traceback.print_exc()

    def _add_changes_sheet(self, handler):
        """在Excel文档中添加变更履历工作表"""
        from openpyxl import Workbook
        
        if not hasattr(handler, 'workbook') or not handler.workbook:
            return

        if '变更履历' in handler.sheet_names:
            del handler.workbook['变更履历']

        new_sheet = handler.workbook.create_sheet('变更履历')
        
        headers = ['序号', '变更时间', '工作表', '行号', '变更类型', 'Q列原值', 'Q列新值', 'R列新值', '实现状态原值', '实现状态新值', '不能实现的原因原值', '不能实现的原因新值', '适用范围']
        new_sheet.append(headers)

        for idx, change in enumerate(self.changes, 1):
            row = [
                idx,
                change.get('change_time', ''),
                change.get('sheet_name', ''),
                change.get('row', 0),
                change.get('type', ''),
                change.get('old_value', ''),
                change.get('new_value', ''),
                change.get('r_column_new', ''),
                change.get('column_status_original', ''),
                change.get('column_status_new', ''),
                change.get('column_reason_original', ''),
                change.get('column_reason_new', ''),
                change.get('p_column_value', '')
            ]
            new_sheet.append(row)

        for col in new_sheet.columns:
            max_length = 0
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            new_sheet.column_dimensions[col[0].column_letter].width = adjusted_width

    def _append_changes_to_txt(self, file_path):
        """将变更履历追加到文本文件"""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n\n' + '='*60 + '\n')
            f.write('变更履历\n')
            f.write('='*60 + '\n')
            
            for idx, change in enumerate(self.changes, 1):
                f.write(f"\n第 {idx} 项变更:\n")
                f.write(f"  时间: {change.get('change_time', '')}\n")
                f.write(f"  工作表: {change.get('sheet_name', '')}\n")
                f.write(f"  行号: {change.get('row', 0)}\n")
                f.write(f"  类型: {change.get('type', '')}\n")
                f.write(f"  Q列原值: {change.get('old_value', '')}\n")
                f.write(f"  Q列新值: {change.get('new_value', '')}\n")
                f.write(f"  R列新值: {change.get('r_column_new', '')}\n")
                f.write(f"  适用范围: {change.get('p_column_value', '')}\n")

    def export_changes(self):
        if not self.changes:
            QMessageBox.warning(self, '警告', '没有可导出的变更履历')
            return

        file_path, _ = QFileDialog.getSaveFileName(self, '导出变更履历', '',
                                                  'Excel工作簿 (*.xlsx);;JSON文件 (*.json);;文本文件 (*.txt)')

        if file_path:
            try:
                from utils import export_changes_to_excel, export_changes_to_json, export_changes_to_txt

                ext = file_path.split('.')[-1].lower()

                if ext == 'xlsx':
                    export_changes_to_excel(self.changes, file_path)
                elif ext == 'json':
                    export_changes_to_json(self.changes, file_path)
                else:
                    export_changes_to_txt(self.changes, file_path)

                QMessageBox.information(self, '成功', f'变更履历已导出至:\n{file_path}')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导出失败:\n{str(e)}')

    def show_marking_rules(self):
        rules_dialog = QDialog(self)
        rules_dialog.setWindowTitle('打点规则详情')
        rules_dialog.resize(600, 400)

        layout = QVBoxLayout(rules_dialog)

        title_label = QLabel('内置打点规则')
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        rules_text = QTextEdit()
        rules_text.setReadOnly(True)
        rules_text.setText("""打点规则详情

规则名称：ID匹配打点规则

适用场景：
- SWRT输入文档包含ID号和打点结果列
- SWRT平台文档包含适用范围列和供应商状态列
- 需要根据SWRT输入文档的打点结果更新SWRT平台文档

具体规则：
1. 检查SWRT输入文档的E列（打点结果）
   - 如果E列单元格内容为"否"
   - 提取该行C列的ID号

2. 在SWRT平台文档中查找匹配项
   - 检查P列（适用范围）的内容
   - 如果P列内容包含提取的ID号

3. 执行更新操作
   - 将该行Q列（供应商状态）的值改为"NA"
   - 将P列（适用范围）的内容复制到R列（供应商意见）

规则参数：
- SWRT输入文档触发列：E列（打点结果）
- 触发条件值："否"
- ID提取列：C列
- SWRT平台文档匹配列：P列（适用范围）
- 修改目标列：Q列（供应商状态）
- 目标值："NA"
- 复制目标列：R列（供应商意见）


版本：v1.0
更新时间：2026-05-03
""")
        layout.addWidget(rules_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(rules_dialog.accept)
        layout.addWidget(buttons)

        rules_dialog.exec_()

    def show_help(self):
        QMessageBox.about(self, '帮助',
            'SWRT文档内容更新软件 v1.3\n\n'
            '基于SWRT输入文档，自动在SWRT平台文档进行打点，生成更新后的文档\n\n'
            '使用步骤：\n'
            '1. 导入SWRT输入文档和SWRT平台文档\n'
            '2. 对文档进行检查确保数据完整\n'
            '3. 点击"执行打点"按钮\n'
            '4. 导出更新后的文档\n\n'
            '支持格式: .xlsx, .docx, .pdf, .txt')

    def show_about(self):
        QMessageBox.about(self, '关于',
            'SWRT文档内容更新软件 v1.3\n\n'
            '基于SWRT输入文档，自动在SWRT平台文档进行打点，生成更新后的文档\n\n'
            '支持格式: .xlsx, .docx, .pdf, .txt\n\n'
            '功能特点:\n'
            '- 文档完整性检查\n'
            '- 智能打点匹配\n'
            '- 变更履历记录\n'
            '- 多格式文档导出')
