# -*- coding: utf-8 -*-
"""
智能刷题系统 - 移动端版本 (Kivy)
支持打包成Android APK在鸿蒙系统运行
"""

import random
import re
import os
import time
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore

# 设置窗口背景色
Window.clearcolor = (0.97, 0.97, 0.97, 1)

# ===================== 题库数据（内嵌）=====================
# 由于移动端无法直接读取docx文件，需要将题库转换为JSON格式
DEFAULT_QUESTIONS = [
    # 示例题目，实际使用时需要替换为完整题库
    {
        "type": "单选题",
        "question": "这是示例单选题，实际使用时请将题库.docx转换为questions.json文件",
        "answer": "A",
        "note": "解析：请在电脑上将题库.docx转换为JSON格式后导入"
    }
]

class QuestionData:
    """题库数据管理类"""
    
    def __init__(self):
        self.all_data = []
        self.question_types = {"单选题": [], "多选题": [], "判断题": []}
        self.wrong_questions = []
        self.load_data()
        self.load_wrong_questions()
    
    def load_data(self):
        """加载题库数据"""
        # 尝试从多个位置加载数据
        possible_paths = [
            'questions.json',  # 当前目录
            os.path.join(os.path.dirname(__file__), 'questions.json'),
            '/sdcard/Download/questions.json',  # Android下载目录
            '/storage/emulated/0/Download/questions.json',
        ]
        
        data = None
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"成功加载题库: {path}")
                    break
                except Exception as e:
                    print(f"加载失败 {path}: {e}")
                    continue
        
        if data:
            self.all_data = data
        else:
            self.all_data = DEFAULT_QUESTIONS
            print("使用默认示例题库")
        
        # 分类题目
        self.categorize_questions()
    
    def categorize_questions(self):
        """按题型分类题目"""
        self.question_types = {"单选题": [], "多选题": [], "判断题": []}
        for q in self.all_data:
            q_type = q.get('type', '单选题')
            if q_type in self.question_types:
                self.question_types[q_type].append(q)
    
    def load_wrong_questions(self):
        """从本地存储加载错题"""
        try:
            store = JsonStore('wrong_questions.json')
            if store.exists('wrong'):
                self.wrong_questions = store.get('wrong')['data']
        except:
            self.wrong_questions = []
    
    def save_wrong_questions(self):
        """保存错题到本地"""
        try:
            store = JsonStore('wrong_questions.json')
            store.put('wrong', data=self.wrong_questions)
        except Exception as e:
            print(f"保存错题失败: {e}")
    
    def add_wrong_question(self, question):
        """添加错题"""
        if question not in self.wrong_questions:
            self.wrong_questions.append(question)
            self.save_wrong_questions()
    
    def clear_wrong_questions(self):
        """清空错题"""
        self.wrong_questions = []
        self.save_wrong_questions()


# ===================== 主界面 =====================
class QuizScreen(Screen):
    """答题界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question_data = QuestionData()
        self.current = None
        self.user_answer = None
        self.exam_mode = False
        self.start_time = 0
        self.pool = []
        self.timer_event = None
        
        self.build_ui()
    
    def build_ui(self):
        """构建UI界面"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # 顶部信息栏
        top_bar = BoxLayout(size_hint_y=0.08, spacing=10)
        self.type_label = Label(
            text='【随机刷题】',
            font_size='18sp',
            color=(0, 0.34, 0.7, 1),
            bold=True,
            size_hint_x=0.6
        )
        self.timer_label = Label(
            text='',
            font_size='14sp',
            color=(0.85, 0.12, 0.02, 1),
            size_hint_x=0.4
        )
        top_bar.add_widget(self.type_label)
        top_bar.add_widget(self.timer_label)
        main_layout.add_widget(top_bar)
        
        # 题目区域（可滚动）
        scroll = ScrollView(size_hint_y=0.45)
        self.question_label = Label(
            text='点击"下一题"开始',
            font_size='16sp',
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            text_size=(Window.width - 40, None),
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        self.question_label.bind(texture_size=self._update_label_height)
        scroll.add_widget(self.question_label)
        main_layout.add_widget(scroll)
        
        # 选项区域
        self.options_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.25)
        self.option_buttons = {}
        
        # 单选题/多选题选项按钮
        for opt in ['A', 'B', 'C', 'D']:
            btn = ToggleButton(
                text=opt,
                font_size='18sp',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda x, v=opt: self.on_option_select(v))
            self.option_buttons[opt] = btn
            self.options_layout.add_widget(btn)
        
        # 判断题选项
        self.judge_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.25)
        for opt in ['对', '错']:
            btn = ToggleButton(
                text=opt,
                font_size='18sp',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda x, v=opt: self.on_option_select(v))
            self.option_buttons[opt] = btn
            self.judge_layout.add_widget(btn)
        
        main_layout.add_widget(self.options_layout)
        
        # 结果显示
        self.result_label = Label(
            text='',
            font_size='16sp',
            size_hint_y=0.08
        )
        main_layout.add_widget(self.result_label)
        
        # 答案和解析区域
        scroll_answer = ScrollView(size_hint_y=0.2)
        self.answer_text = Label(
            text='',
            font_size='14sp',
            color=(0.75, 0, 0, 1),
            size_hint_y=None,
            text_size=(Window.width - 40, None),
            halign='left',
            valign='top'
        )
        self.answer_text.bind(texture_size=self._update_answer_height)
        scroll_answer.add_widget(self.answer_text)
        main_layout.add_widget(scroll_answer)
        
        scroll_note = ScrollView(size_hint_y=0.2)
        self.note_text = Label(
            text='',
            font_size='13sp',
            color=(0, 0.4, 0.13, 1),
            size_hint_y=None,
            text_size=(Window.width - 40, None),
            halign='left',
            valign='top'
        )
        self.note_text.bind(texture_size=self._update_note_height)
        scroll_note.add_widget(self.note_text)
        main_layout.add_widget(scroll_note)
        
        # 底部按钮栏
        btn_bar = BoxLayout(size_hint_y=0.1, spacing=10)
        
        self.next_btn = Button(
            text='下一题',
            font_size='16sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        self.next_btn.bind(on_press=lambda x: self.next_question())
        
        self.show_btn = Button(
            text='显示答案',
            font_size='16sp',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        self.show_btn.bind(on_press=lambda x: self.show_answer())
        
        btn_bar.add_widget(self.show_btn)
        btn_bar.add_widget(self.next_btn)
        main_layout.add_widget(btn_bar)
        
        self.add_widget(main_layout)
        
        # 初始化
        self.mode_random()
    
    def _update_label_height(self, instance, value):
        instance.height = instance.texture_size[1] + 20
    
    def _update_answer_height(self, instance, value):
        instance.height = instance.texture_size[1] + 10
    
    def _update_note_height(self, instance, value):
        instance.height = instance.texture_size[1] + 10
    
    def clear_options(self):
        """清除选项选中状态"""
        for btn in self.option_buttons.values():
            btn.state = 'normal'
            btn.background_color = (0.9, 0.9, 0.9, 1)
    
    def on_option_select(self, value):
        """选项选择处理"""
        self.user_answer = value
        self.clear_options()
        self.option_buttons[value].state = 'down'
        self.option_buttons[value].background_color = (0.3, 0.7, 1, 1)
        self.check_answer(value)
    
    def check_answer(self, value):
        """检查答案"""
        if not self.current:
            return
        
        correct = (value.upper() == self.current['answer'].upper())
        
        if correct:
            self.result_label.text = f'你选：{value}  ✅ 正确'
            self.result_label.color = (0.18, 0.55, 0.34, 1)
        else:
            self.result_label.text = f'你选：{value}  ❌ 错误'
            self.result_label.color = (0.8, 0.15, 0.15, 1)
            self.question_data.add_wrong_question(self.current)
        
        self.show_answer()
    
    def show_answer(self):
        """显示答案和解析"""
        if not self.current:
            return
        self.answer_text.text = f"正确答案：{self.current['answer']}"
        self.note_text.text = f"解析：{self.current.get('note', '无解析')}"
    
    def update_timer(self, dt):
        """更新计时器"""
        if self.exam_mode:
            used = int(time.time() - self.start_time)
            self.timer_label.text = f"考试用时：{used//60}分{used%60}秒"
    
    def mode_random(self):
        """随机刷题模式"""
        self.exam_mode = False
        self.timer_label.text = ''
        self.type_label.text = '【随机刷题】'
        self.pool = self.question_data.all_data.copy()
        if self.timer_event:
            self.timer_event.cancel()
        self.next_question()
    
    def mode_type(self, q_type):
        """按题型刷题"""
        self.exam_mode = False
        self.timer_label.text = ''
        self.type_label.text = f'【{q_type}】'
        self.pool = self.question_data.question_types.get(q_type, []).copy()
        if self.timer_event:
            self.timer_event.cancel()
        self.next_question()
    
    def mode_wrong(self):
        """错题重做模式"""
        self.exam_mode = False
        self.timer_label.text = ''
        self.type_label.text = '【错题重做】'
        self.pool = self.question_data.wrong_questions.copy()
        if self.timer_event:
            self.timer_event.cancel()
        
        if not self.pool:
            self.show_popup('提示', '暂无错题')
            self.mode_random()
        else:
            self.next_question()
    
    def mode_exam(self):
        """模拟考试模式"""
        self.exam_mode = True
        self.start_time = time.time()
        self.type_label.text = '【模拟考试】'
        self.pool = random.sample(
            self.question_data.all_data,
            min(50, len(self.question_data.all_data))
        )
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        self.next_question()
    
    def next_question(self):
        """下一题"""
        if not self.pool:
            self.show_popup('提示', '已全部答完！')
            return
        
        self.current = random.choice(self.pool)
        self.pool.remove(self.current)
        
        self.user_answer = None
        self.clear_options()
        
        # 更新题目显示
        q_type = self.current.get('type', '单选题')
        question_text = self.current.get('question', '')
        self.question_label.text = f"[{q_type}]\n\n{question_text}"
        
        # 根据题型显示不同选项
        self.result_label.text = ''
        self.answer_text.text = ''
        self.note_text.text = ''
        
        # 切换选项布局
        parent = self.options_layout.parent
        if q_type == '判断题':
            if self.options_layout in parent.children:
                parent.remove_widget(self.options_layout)
            if self.judge_layout not in parent.children:
                parent.add_widget(self.judge_layout, index=2)
        else:
            if self.judge_layout in parent.children:
                parent.remove_widget(self.judge_layout)
            if self.options_layout not in parent.children:
                parent.add_widget(self.options_layout, index=2)
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=message, font_size='16sp'),
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )
        popup.open()


class MenuScreen(Screen):
    """菜单界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text='智能刷题系统',
            font_size='28sp',
            color=(0, 0.34, 0.7, 1),
            bold=True,
            size_hint_y=0.15
        )
        layout.add_widget(title)
        
        # 按钮区域
        btn_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.7)
        
        buttons = [
            ('随机刷题', self.go_random),
            ('单选题', lambda: self.go_type('单选题')),
            ('多选题', lambda: self.go_type('多选题')),
            ('判断题', lambda: self.go_type('判断题')),
            ('错题重做', self.go_wrong),
            ('模拟考试', self.go_exam),
        ]
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                font_size='18sp',
                background_color=(0.2, 0.6, 1, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=callback)
            btn_layout.add_widget(btn)
        
        layout.add_widget(btn_layout)
        
        # 统计信息
        self.info_label = Label(
            text='加载中...',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.15
        )
        layout.add_widget(self.info_label)
        
        self.add_widget(layout)
        
        # 延迟更新统计
        Clock.schedule_once(self.update_info, 0.5)
    
    def update_info(self, dt):
        """更新统计信息"""
        try:
            qd = QuestionData()
            total = len(qd.all_data)
            wrong = len(qd.wrong_questions)
            self.info_label.text = f'总题数：{total}  |  错题数：{wrong}'
        except:
            self.info_label.text = '题库加载失败'
    
    def go_random(self, instance):
        self.manager.get_screen('quiz').mode_random()
        self.manager.current = 'quiz'
    
    def go_type(self, q_type):
        self.manager.get_screen('quiz').mode_type(q_type)
        self.manager.current = 'quiz'
    
    def go_wrong(self, instance):
        self.manager.get_screen('quiz').mode_wrong()
        self.manager.current = 'quiz'
    
    def go_exam(self, instance):
        self.manager.get_screen('quiz').mode_exam()
        self.manager.current = 'quiz'


class QuizApp(App):
    """主应用类"""
    
    def build(self):
        # 设置窗口标题（桌面端）
        self.title = '智能刷题系统'
        
        # 创建屏幕管理器
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(QuizScreen(name='quiz'))
        
        return sm


def convert_docx_to_json(docx_path, json_path):
    """
    将docx题库转换为JSON格式
    在电脑上运行此函数来转换题库
    """
    try:
        import docx
        
        doc = docx.Document(docx_path)
        full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
        
        pattern = re.compile(
            r"(【单选题】|【多选题】|【判断题】)(.*?)"
            r"正确答案[：\s]+([A-Za-z0-9]+).*?"
            r"(题目解析[：\s]+.*?)?(?=【单选|【多选|【判断|$)",
            re.DOTALL
        )
        
        qa_list = []
        for item in pattern.findall(full_text):
            t = item[0].strip("【】")
            q = item[1].strip()
            ans = item[2].strip().upper()
            note = (item[3] or "无解析").replace("题目解析", "解析").strip()
            if q and ans:
                qa_list.append({
                    "type": t,
                    "question": q,
                    "answer": ans,
                    "note": note
                })
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(qa_list, f, ensure_ascii=False, indent=2)
        
        print(f"转换完成！共 {len(qa_list)} 题")
        return qa_list
        
    except ImportError:
        print("请先安装python-docx: pip install python-docx")
        return []
    except Exception as e:
        print(f"转换失败: {e}")
        return []


if __name__ == '__main__':
    # 如果是Windows/Mac/Linux桌面环境，先转换题库
    if platform in ('win', 'linux', 'macosx'):
        if os.path.exists('题库.docx'):
            print("检测到题库.docx，正在转换为JSON格式...")
            convert_docx_to_json('题库.docx', 'questions.json')
    
    QuizApp().run()
