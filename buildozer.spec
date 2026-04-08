[app]

# 应用标题
title = 智能刷题系统

# 包名（小写，用点分隔）
package.name = tikuapp

# 包域名（反向域名格式）
package.domain = com.example

# 源代码目录
source.dir = .

# 主程序文件
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# 版本号
version = 1.0.0

# 应用要求
requirements = python3,kivy==2.2.1

# 图标（如果有的话）
# icon.filename = %(source.dir)s/icon.png

# 是否全屏
fullscreen = 0

# Android API版本
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# 支持的ABI架构（鸿蒙系统兼容arm64-v8a和armeabi-v7a）
android.archs = arm64-v8a, armeabi-v7a

# 权限声明
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# 应用方向
orientation = portrait

# 是否使用AndroidX
android.useAndroidX = True

# 是否启用SQLite
android.enable_androidx = True

# 添加Python标准库
android.add_libs_arm64_v8a = 
android.add_libs_armeabi_v7a = 

# 保留Python标准库
android.copy_libs = 1

# 打包模式（release或debug）
android.release_artifact = apk

# 签名配置（发布时需要）
# android.keystore = 
# android.keystore_path = 
# android.keystore_password = 
# android.keyalias = 
# android.keyalias_password = 

[buildozer]

# 构建目录
build_dir = ./.buildozer

# 是否使用虚拟环境
bin_dir = ./bin

# 日志级别
log_level = 2

# 是否警告未在spec中定义的根目录文件
warn_on_root = 1
