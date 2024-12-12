import sys
import os
import shutil
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from heatmap import generate_heatmap
from diagnose import diagnose

class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.photos_path = []   # 所有打开的图片的路径
        self.idx = -1   # 当前打开的图片的编号
        self.heatmap_status = False   # False表示当前显示的是原图，True表示当前显示的是热图

        self.setWindowTitle("眼底彩照辅助诊断工具")
        self.resize(1800, 900)
        self.setWindowIcon(QIcon("icon.png"))

        # 菜单栏
        self.menubar = self.menuBar()
        self.menubar.setFont(QFont("微软雅黑", 12))

        file_menu = self.menubar.addMenu("文件")
        # 载入眼底彩照
        self.load_action = QAction("载入眼底彩照", self)
        self.load_action.triggered.connect(self.load_photos)
        file_menu.addAction(self.load_action)
        file_menu.addSeparator()
        # 上一张
        self.previous_action = QAction("上一张", self)
        self.previous_action.triggered.connect(self.previous_photo)
        self.previous_action.setEnabled(False)
        file_menu.addAction(self.previous_action)
        # 下一张
        self.after_action = QAction("下一张", self)
        self.after_action.triggered.connect(self.after_photo)
        self.after_action.setEnabled(False)
        file_menu.addAction(self.after_action)
        file_menu.addSeparator()
        # 保存诊断结果
        self.save_text_action = QAction('保存诊断结果', self)
        self.save_text_action.triggered.connect(self.save_text)
        self.save_text_action.setEnabled(False)
        file_menu.addAction(self.save_text_action)
        # 保存病灶热图
        self.save_heatmap_action = QAction('保存病灶热图', self)
        self.save_heatmap_action.triggered.connect(self.save_heatmap)
        self.save_heatmap_action.setEnabled(False)
        file_menu.addAction(self.save_heatmap_action)

        diagnose_menu = self.menubar.addMenu("诊断")
        # 糖尿病视网膜病病变分级
        self.diagnose_dr_action = QAction('糖尿病视网膜病病变分级', self)
        self.diagnose_dr_action.triggered.connect(lambda: self.__diagnose('糖尿病视网膜病病变分级'))
        self.diagnose_dr_action.setEnabled(False)
        diagnose_menu.addAction(self.diagnose_dr_action)
        # 青光眼诊断
        self.diagnose_g_action = QAction('青光眼诊断', self)
        self.diagnose_g_action.triggered.connect(lambda: self.__diagnose('青光眼'))
        self.diagnose_g_action.setEnabled(False)
        diagnose_menu.addAction(self.diagnose_g_action)
        # 多疾病诊断
        self.diagnose_all_action = QAction('多疾病诊断', self)
        self.diagnose_all_action.triggered.connect(lambda: self.__diagnose('多疾病'))
        self.diagnose_all_action.setEnabled(False)
        diagnose_menu.addAction(self.diagnose_all_action)

        heatmap_menu = self.menubar.addMenu("热图")
        # 切换原图/热图
        self.switch_action = QAction('切换原图/热图', self)
        self.switch_action.triggered.connect(self.switch)
        self.switch_action.setEnabled(False)
        heatmap_menu.addAction(self.switch_action)
        heatmap_menu.addSeparator()
        # 计算病灶热图
        self.cam_action = QAction('计算病灶热图', self)
        self.cam_action.triggered.connect(self.generate_heatmap)
        self.cam_action.setEnabled(False)
        heatmap_menu.addAction(self.cam_action)

        all_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.setStretch(0, 1)
        left_layout.setStretch(1, 1)
        left_layout.setStretch(2, 1)
        left_layout.setStretch(3, 1)
        middle_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        all_layout.addLayout(left_layout)
        all_layout.addLayout(middle_layout)
        all_layout.addLayout(right_layout)
        all_layout.setStretch(0, 1)
        all_layout.setStretch(1, 2)
        all_layout.setStretch(2, 1)

        disease_select_layout = QVBoxLayout()
        left_layout.addLayout(disease_select_layout)
        diabetes_select = QRadioButton("糖尿病视网膜病病变分级")
        glaucoma_select = QRadioButton("青光眼诊断")
        all_select = QRadioButton("多疾病诊断")
        self.disease_select_group = QButtonGroup(disease_select_layout)
        self.disease_select_group.addButton(diabetes_select, 11)
        self.disease_select_group.addButton(glaucoma_select, 12)
        self.disease_select_group.addButton(all_select, 13)
        diabetes_select.setChecked(True)
        disease_select_layout.addWidget(diabetes_select)
        disease_select_layout.addWidget(glaucoma_select)
        disease_select_layout.addWidget(all_select)
        
        button_layout_1 = QVBoxLayout()
        left_layout.addLayout(button_layout_1)
        # 开始诊断按钮
        self.diagnose_button = QPushButton("开始诊断")
        self.diagnose_button.setEnabled(False)
        self.diagnose_button.clicked.connect(self.diagnose)
        button_layout_1.addWidget(self.diagnose_button)
        # 保存诊断结果按钮
        self.save_text_button = QPushButton("保存诊断结果")
        self.save_text_button.setEnabled(False)
        self.save_text_button.clicked.connect(self.save_text)
        button_layout_1.addWidget(self.save_text_button)

        cam_select_layout = QVBoxLayout()
        left_layout.addLayout(cam_select_layout)
        gradcam_select = QRadioButton("GradCAM")
        gradcamplus_select = QRadioButton("GradCAM++")
        smoothgradcamplus_select = QRadioButton("Smooth GradCAM++")
        scorecam_select = QRadioButton("ScoreCAM")
        sscam_select = QRadioButton("SSCAM")
        self.cam_select_group = QButtonGroup(cam_select_layout)
        self.cam_select_group.addButton(gradcam_select, 21)
        self.cam_select_group.addButton(gradcamplus_select, 22)
        self.cam_select_group.addButton(smoothgradcamplus_select, 23)
        self.cam_select_group.addButton(scorecam_select, 24)
        self.cam_select_group.addButton(sscam_select, 25)
        gradcam_select.setChecked(True)
        cam_select_layout.addWidget(gradcam_select)
        cam_select_layout.addWidget(gradcamplus_select)
        cam_select_layout.addWidget(smoothgradcamplus_select)
        cam_select_layout.addWidget(scorecam_select)
        cam_select_layout.addWidget(sscam_select)

        button_layout_2 = QVBoxLayout()
        left_layout.addLayout(button_layout_2)
        # 计算病灶热图按钮
        self.heatmap_button = QPushButton("计算病灶热图")
        self.heatmap_button.setEnabled(False)
        self.heatmap_button.clicked.connect(self.generate_heatmap)
        button_layout_2.addWidget(self.heatmap_button)
        # 切换原图/热图按钮
        self.switch_button = QPushButton("切换原图/热图")
        self.switch_button.setEnabled(False)
        self.switch_button.clicked.connect(self.switch)
        button_layout_2.addWidget(self.switch_button)
        # 保存病灶热图按钮
        self.save_heatmap_button = QPushButton("保存病灶热图")
        self.save_heatmap_button.setEnabled(False)
        self.save_heatmap_button.clicked.connect(self.save_heatmap)
        button_layout_2.addWidget(self.save_heatmap_button)
        
        button_layout_3 = QHBoxLayout()
        middle_layout.addLayout(button_layout_3)
        # 载入眼底彩照按钮
        self.load_button = QPushButton("载入眼底彩照")
        self.load_button.clicked.connect(self.load_photos)
        button_layout_3.addWidget(self.load_button)
        # 上一张按钮
        self.previous_button = QPushButton("上一张")
        self.previous_button.clicked.connect(self.previous_photo)
        self.previous_button.setEnabled(False)
        button_layout_3.addWidget(self.previous_button)
        # 下一张按钮
        self.after_button = QPushButton("下一张")
        self.after_button.clicked.connect(self.after_photo)
        self.after_button.setEnabled(False)
        button_layout_3.addWidget(self.after_button)
        
        # 显示图片的QLabel
        self.photo = QLabel()
        self.photo.setAlignment(Qt.AlignCenter)
        # self.photo.setStyleSheet("background-color:White")
        middle_layout.addWidget(self.photo)

        # 显示诊断结果的文本框
        self.diagnose_result = QTextEdit()
        right_layout.addWidget(self.diagnose_result)

        widget = QWidget()
        widget.setFont(QFont("宋体", 16))
        widget.setLayout(all_layout)
        self.setCentralWidget(widget)
    
    def load_photos(self):
        self.photos_path, _ = QFileDialog.getOpenFileNames(self, '选择眼底彩照', filter='图片 (*.png *.jpg *.jpeg *.ppm )')

        if self.photos_path != []:
            self.idx = 0
            self.__load_photo(0)

            self.previous_action.setEnabled(True)
            self.after_action.setEnabled(True)
            self.save_text_action.setEnabled(True)
            self.diagnose_dr_action.setEnabled(True)
            self.diagnose_g_action.setEnabled(True)
            self.diagnose_all_action.setEnabled(True)
            self.switch_action.setEnabled(True)
            self.cam_action.setEnabled(True)

            self.diagnose_button.setEnabled(True)
            self.save_text_button.setEnabled(True)
            self.heatmap_button.setEnabled(True)
            self.switch_button.setEnabled(True)
            self.previous_button.setEnabled(True)
            self.after_button.setEnabled(True)

    def __load_photo(self, idx):
        if idx >= 0 and idx < len(self.photos_path):
            image = QPixmap(self.photos_path[idx])
            image = self.__scale_photo(image)
            self.photo.setPixmap(image)

            self.heatmap_status = False

    def __load_heatmap(self, idx):
        if self.cam_select_group.checkedId() == 21:
            heatmap_type = "GradCAM"
        elif self.cam_select_group.checkedId() == 22:
            heatmap_type = "GradCAM++"
        elif self.cam_select_group.checkedId() == 23:
            heatmap_type = "SmoothGradCAM++"
        elif self.cam_select_group.checkedId() == 24:
            heatmap_type = "ScoreCAM"
        elif self.cam_select_group.checkedId() == 25:
            heatmap_type = "SSCAM"
        else:
            return
        
        image_name = self.photos_path[idx].split("/")[-1]
        suffix = image_name.split(".")[-1]
        heatmap_path = "./热图/" + image_name.split(".")[0] + "_" + heatmap_type + "." + suffix

        image = QPixmap(heatmap_path)
        image = self.__scale_photo(image)
        self.photo.setPixmap(image)

        self.heatmap_status = True

    def __scale_photo(self, image):
        width = image.width()
        height = image.height()

        label_width = self.photo.width()
        label_height = self.photo.height()

        width_ratio = width / label_width
        height_ratio = height / label_height

        if width_ratio >= height_ratio:
            image = image.scaled(round(width / width_ratio), round(height / width_ratio))
        else:
            image = image.scaled(round(width / height_ratio), round(height / height_ratio))

        return image
    
    def previous_photo(self):
        if self.idx == -1:
            return
        
        if self.idx == 0:
            self.idx = len(self.photos_path) - 1
        else:
            self.idx -= 1
        
        if self.heatmap_status == False or (self.heatmap_status == True and self.__check_heatmap() == False):
            self.__load_photo(self.idx)
        else:
            self.__load_heatmap(self.idx)

    def after_photo(self):
        if self.idx == -1:
            return
        
        if self.idx == len(self.photos_path) - 1:
            self.idx = 0
        else:
            self.idx += 1
        
        if self.heatmap_status == False or (self.heatmap_status == True and self.__check_heatmap() == False):
            self.__load_photo(self.idx)
        else:
            self.__load_heatmap(self.idx)

    def diagnose(self):
        if self.disease_select_group.checkedId() == 11:
            self.__diagnose("糖尿病视网膜病病变分级")
        elif self.disease_select_group.checkedId() == 12:
            self.__diagnose("青光眼")
        elif self.disease_select_group.checkedId() == 13:
            self.__diagnose("多疾病")
        else:
            return

    def __diagnose(self, diagnose_type):
        text = diagnose(diagnose_type, self.photos_path[self.idx])
        self.diagnose_result.setText(text)

    def save_text(self):
        text = self.diagnose_result.toPlainText()
        
        if text == "":
            QMessageBox.warning(self, "错误", "诊断结果为空！")
        else:
            directory = QFileDialog.getExistingDirectory(self, "选择保存路径")
            
            f = open(directory + '\\诊断结果.txt','w')
            print(text, file=f)
            f.close()

    def __check_heatmap(self):
        if self.cam_select_group.checkedId() == 21:
            heatmap_type = "GradCAM"
        elif self.cam_select_group.checkedId() == 22:
            heatmap_type = "GradCAM++"
        elif self.cam_select_group.checkedId() == 23:
            heatmap_type = "SmoothGradCAM++"
        elif self.cam_select_group.checkedId() == 24:
            heatmap_type = "ScoreCAM"
        elif self.cam_select_group.checkedId() == 25:
            heatmap_type = "SSCAM"
        else:
            return
        
        image_name = self.photos_path[self.idx].split("/")[-1]
        suffix = image_name.split(".")[-1]
        heatmap_path = "./热图/" + image_name.split(".")[0] + "_" + heatmap_type + "." + suffix
        
        return os.path.exists(heatmap_path)
    
    def generate_heatmap(self):
        if self.disease_select_group.checkedId() == 11:
            diagnose_type = "糖尿病视网膜病病变分级"
        elif self.disease_select_group.checkedId() == 12:
            diagnose_type = "青光眼"
        elif self.disease_select_group.checkedId() == 13:
            diagnose_type = "多疾病"
        else:
            return
        
        if self.cam_select_group.checkedId() == 21:
            heatmap_type = "GradCAM"
        elif self.cam_select_group.checkedId() == 22:
            heatmap_type = "GradCAM++"
        elif self.cam_select_group.checkedId() == 23:
            heatmap_type = "SmoothGradCAM++"
        elif self.cam_select_group.checkedId() == 24:
            heatmap_type = "ScoreCAM"
        elif self.cam_select_group.checkedId() == 25:
            heatmap_type = "SSCAM"
        else:
            return
        
        generate_heatmap(diagnose_type, heatmap_type, self.photos_path[self.idx])

        self.__load_heatmap(self.idx)
        self.save_heatmap_action.setEnabled(True)
        self.save_heatmap_button.setEnabled(True)

    def switch(self):
        if self.__check_heatmap() == False:
            return
        elif self.heatmap_status == True:
            self.__load_photo(self.idx)
        else:
            self.__load_heatmap(self.idx)

    def save_heatmap(self):
        if self.heatmap_status == False:
            return
        elif self.__check_heatmap() == False:
            QMessageBox.warning(self, "错误", "未生成热图！")
        else:
            directory = QFileDialog.getExistingDirectory(self, "选择保存路径")

            if self.cam_select_group.checkedId() == 21:
                heatmap_type = "GradCAM"
            elif self.cam_select_group.checkedId() == 22:
                heatmap_type = "GradCAM++"
            elif self.cam_select_group.checkedId() == 23:
                heatmap_type = "SmoothGradCAM++"
            elif self.cam_select_group.checkedId() == 24:
                heatmap_type = "ScoreCAM"
            elif self.cam_select_group.checkedId() == 25:
                heatmap_type = "SSCAM"
            else:
                return

            image_name = self.photos_path[self.idx].split("/")[-1]
            suffix = image_name.split(".")[-1]
            heatmap_path = "./热图/" + image_name.split(".")[0] + "_" + heatmap_type + "." + suffix
            new_path = directory + "\\" + heatmap_path.split("/")[-1]
            shutil.copy(heatmap_path, new_path)
            

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec_())