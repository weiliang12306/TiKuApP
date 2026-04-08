# 智能刷题APP

基于Kivy框架开发的移动端刷题应用，支持Android和鸿蒙系统。

## 📱 功能特点

- ✅ 随机刷题
- ✅ 按题型刷题（单选题、多选题、判断题）
- ✅ 错题重做
- ✅ 模拟考试（50题计时模式）
- ✅ 答案解析
- ✅ 错题本地保存

## 📦 题库数据

- 总题数：4155道
  - 单选题：1542道
  - 判断题：1840道
  - 多选题：773道

## 🚀 快速开始

### 下载APK

1. 点击右侧的 **Releases**
2. 下载最新的APK文件
3. 在手机上安装即可使用

### 安装到鸿蒙/安卓手机

1. 将APK传输到手机
2. 设置 → 安全 → 允许安装未知来源应用
3. 点击安装

## 🛠️ 自行打包

如果你想自己打包APK：

### 方法1：使用GitHub Actions（推荐）

1. Fork 这个仓库
2. 修改代码或题库
3. Push 到 main 分支
4. 等待GitHub Actions自动构建
5. 在 Actions 页面下载APK

### 方法2：本地打包

需要Linux环境或WSL：

```bash
# 安装依赖
pip install buildozer cython

# 打包APK
buildozer android debug
```

## 📁 项目结构

```
.
├── main.py              # 主程序
├── buildozer.spec       # 打包配置
├── questions.json       # 题库数据
├── convert_tiku.py      # 题库转换工具
└── .github/
    └── workflows/
        └── build-apk.yml    # GitHub Actions配置
```

## 📝 更新题库

如果你有新的Word格式题库：

1. 将Word文件命名为 `题库.docx`
2. 运行 `python convert_tiku.py`
3. 生成新的 `questions.json`
4. 重新打包APK

## 🔧 技术栈

- Python 3.10+
- Kivy 2.2.1
- Buildozer
- Android API 33

## 📄 许可证

MIT License

## 💡 提示

- 首次启动可能需要几秒钟加载题库
- 错题会自动保存在手机本地
- 支持横竖屏切换

---

**祝你学习顺利！** 🎉
