import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QProgressBar,
                            QMessageBox, QListWidgetItem, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class UninstallThread(QThread):
    """卸载应用的线程，避免界面卡顿"""
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, package_full_name):
        super().__init__()
        self.package_full_name = package_full_name
        
    def run(self):
        try:
            # 使用PowerShell命令卸载应用
            cmd = f'powershell -Command "Remove-AppxPackage {self.package_full_name}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.finished.emit(True, f"成功卸载: {self.package_full_name}")
            else:
                error_msg = f"卸载失败: {result.stderr}"
                self.finished.emit(False, error_msg)
        except Exception as e:
            self.finished.emit(False, f"发生错误: {str(e)}")

class AppxUninstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_apps()
        
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("UWP应用卸载工具")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f3f3;
            }
            QLabel {
                color: #333333;
                font-family: 'Segoe UI', 'Microsoft YaHei';
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px 20px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 1px solid #999999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999999;
                border: 1px solid #dddddd;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 14px;
                alternate-background-color: #f9f9f9;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-size: 14px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        
        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加标题
        title_label = QLabel("UWP应用卸载工具")
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 10px; color: #0078d4;")
        main_layout.addWidget(title_label)
        
        # 添加搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索应用:")
        search_label.setFont(QFont("Microsoft YaHei", 14))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入应用名称搜索...")
        self.search_input.setFont(QFont("Microsoft YaHei", 14))
        self.search_input.textChanged.connect(self.filter_apps)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        
        # 添加应用列表
        list_label = QLabel("已安装的应用:")
        list_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        main_layout.addWidget(list_label)
        
        self.app_list = QListWidget()
        self.app_list.setFont(QFont("Microsoft YaHei", 16))
        self.app_list.setAlternatingRowColors(True)
        self.app_list.setSelectionMode(QListWidget.SingleSelection)
        self.app_list.setSpacing(2)
        self.app_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
                outline: 0px;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 6px;
                border: none;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(self.app_list)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.refresh_button = QPushButton("刷新列表")
        self.refresh_button.setFont(QFont("Microsoft YaHei", 14))
        self.refresh_button.clicked.connect(self.load_apps)
        self.refresh_button.setMinimumHeight(40)
        button_layout.addWidget(self.refresh_button)
        
        self.register_button = QPushButton("注册所有应用")
        self.register_button.setFont(QFont("Microsoft YaHei", 14))
        self.register_button.clicked.connect(self.register_apps)
        self.register_button.setMinimumHeight(40)
        button_layout.addWidget(self.register_button)
        
        self.uninstall_button = QPushButton("卸载选中应用")
        self.uninstall_button.setFont(QFont("Microsoft YaHei", 14))
        self.uninstall_button.clicked.connect(self.uninstall_selected)
        self.uninstall_button.setEnabled(False)  # 初始禁用，选择应用后启用
        self.uninstall_button.setMinimumHeight(40)
        button_layout.addWidget(self.uninstall_button)
        
        main_layout.addLayout(button_layout)
        
        # 添加进度条和状态
        self.status_label = QLabel("就绪")
        self.status_label.setFont(QFont("Microsoft YaHei", 13))
        self.status_label.setStyleSheet("color: #666666; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # 初始隐藏
        self.progress_bar.setFixedHeight(25)
        main_layout.addWidget(self.progress_bar)
        
        # 连接列表选择变化事件
        self.app_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 初始化时注册应用按钮可用
        self.register_button.setEnabled(True)
        
    def _process_app_name(self, app):
        """处理应用名称，优先显示中文名称"""
        # 使用DisplayName如果可用，否则使用Name
        display_name = app.get('DisplayName', app['Name'])
        # 尝试使用PublisherDisplayName来改善中文显示
        publisher_name = app.get('PublisherDisplayName', '')
        
        # 处理资源字符串，如果DisplayName是资源字符串，则使用Name
        if display_name.startswith('ms-resource:'):
            display_name = app['Name']
        
        # 处理PublisherDisplayName的资源字符串
        if publisher_name.startswith('ms-resource:'):
            publisher_name = ''
        
        # 检查名称中是否包含中文字符
        def contains_chinese(text):
            return any('\u4e00' <= char <= '\u9fff' for char in text)
        
        # 如果DisplayName包含中文，直接使用
        if contains_chinese(display_name):
            return display_name
        
        # 如果PublisherDisplayName包含中文且DisplayName是英文，组合显示
        if (publisher_name and 
            contains_chinese(publisher_name) and
            not contains_chinese(display_name)):
            return f"{display_name} ({publisher_name})"
        
        # 如果都包含中文，优先使用PublisherDisplayName
        if (publisher_name and 
            contains_chinese(publisher_name) and
            contains_chinese(display_name)):
            return publisher_name
        
        # 如果PublisherDisplayName包含中文且DisplayName不包含中文，使用PublisherDisplayName
        if (publisher_name and 
            contains_chinese(publisher_name) and
            not contains_chinese(display_name)):
            return publisher_name
        
        # 如果都为英文，使用DisplayName
        return display_name
    
    def load_apps(self):
        """加载所有已安装的Appx包"""
        self.status_label.setText("正在加载应用列表...")
        self.app_list.clear()
        
        try:
            # 使用PowerShell脚本获取所有Appx包及其显示名称
            cmd = 'powershell -ExecutionPolicy Bypass -File "get_appx_packages.ps1"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    apps = json.loads(result.stdout)
                    # 确保是列表形式
                    if not isinstance(apps, list):
                        apps = [apps]
                    
                    # 添加到列表
                    for i, app in enumerate(apps):
                        if "Name" in app and "PackageFullName" in app:
                            # 使用智能名称处理
                            display_name = self._process_app_name(app)
                            
                            item = QListWidgetItem(f"{display_name}")
                            item.setData(Qt.UserRole, app['PackageFullName'])
                            self.app_list.addItem(item)
                        # 更新进度
                        if i % 50 == 0:  # 每50个应用更新一次状态
                            self.status_label.setText(f"正在加载应用列表... ({i}/{len(apps)})")
                            QApplication.processEvents()  # 处理待处理的事件，保持界面响应
                    
                    self.status_label.setText(f"已加载 {self.app_list.count()} 个应用")
                except json.JSONDecodeError:
                    self.status_label.setText("解析应用列表失败")
            else:
                self.status_label.setText(f"获取应用列表失败: {result.stderr}")
        except Exception as e:
            self.status_label.setText(f"加载应用时出错: {str(e)}")
    
    def filter_apps(self):
        """根据搜索框内容过滤应用列表"""
        try:
            search_text = self.search_input.text().lower()
            # 优化搜索性能，避免在大量数据时卡顿
            items = [self.app_list.item(i) for i in range(self.app_list.count())]
            for item in items:
                item.setHidden(search_text not in item.text().lower())
        except Exception as e:
            print(f"搜索功能出错: {e}")
    
    def register_apps(self):
        """注册所有UWP应用，确保所有应用都能被扫描到"""
        reply = QMessageBox.question(self, "确认注册", 
                                    "确定要注册所有UWP应用吗？这将确保所有应用都能被扫描到。",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.status_label.setText("正在注册所有UWP应用...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度
            
            # 禁用按钮防止重复操作
            self.refresh_button.setEnabled(False)
            self.register_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
            
            try:
                # 使用PowerShell命令注册所有UWP应用
                cmd = r'powershell -Command "Get-AppXPackage -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)  # 5分钟超时
                
                if result.returncode == 0:
                    QMessageBox.information(self, "成功", "所有UWP应用已成功注册。请刷新列表以查看更新。")
                    self.status_label.setText("UWP应用注册完成")
                else:
                    error_msg = f"注册失败: {result.stderr}"
                    QMessageBox.critical(self, "失败", error_msg)
                    self.status_label.setText("UWP应用注册失败")
            except subprocess.TimeoutExpired:
                QMessageBox.critical(self, "超时", "注册过程超时，请稍后重试。")
                self.status_label.setText("UWP应用注册超时")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"注册过程中发生错误: {str(e)}")
                self.status_label.setText("UWP应用注册出错")
            finally:
                self.progress_bar.setVisible(False)
                self.refresh_button.setEnabled(True)
                self.register_button.setEnabled(True)
                self.uninstall_button.setEnabled(len(self.app_list.selectedItems()) > 0)
    
    def on_selection_changed(self):
        """当列表选择变化时启用/禁用卸载按钮"""
        self.uninstall_button.setEnabled(len(self.app_list.selectedItems()) > 0)
    
    def uninstall_selected(self):
        """卸载选中的应用"""
        selected_items = self.app_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        app_name = item.text()
        package_full_name = item.data(Qt.UserRole)
        
        # 确认卸载
        reply = QMessageBox.question(self, "确认卸载", 
                                    f"确定要卸载 {app_name} 吗？\n\n包名: {package_full_name}",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.status_label.setText(f"正在卸载 {app_name}...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度
            
            # 禁用按钮防止重复操作
            self.uninstall_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            
            # 创建并启动卸载线程
            self.uninstall_thread = UninstallThread(package_full_name)
            self.uninstall_thread.finished.connect(self.on_uninstall_finished)
            self.uninstall_thread.start()
    
    def on_uninstall_finished(self, success, message):
        """卸载完成后的处理"""
        self.progress_bar.setVisible(False)
        self.refresh_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "成功", message)
            # 刷新应用列表
            self.load_apps()
        else:
            QMessageBox.critical(self, "失败", message)
        
        self.status_label.setText("就绪")

if __name__ == "__main__":
    try:
        # 确保中文显示正常
        app = QApplication(sys.argv)
        font = QFont("SimHei")
        app.setFont(font)
        
        window = AppxUninstaller()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("程序发生错误，请按回车键退出...")