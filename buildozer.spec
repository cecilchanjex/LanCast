[app]

# --- App Info ---
title = LAN Cast Receiver Pro
package.name = lancastreceiver
package.domain = org.lancast
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
orientation = portrait
fullscreen = 1

# Python & Kivy requirements
requirements = python3,kivy,opencv-python

# Permissions
android.permissions = INTERNET,WAKE_LOCK

# --- Android Specific ---
# Target architectures
android.archs = arm64-v8a, armeabi-v7a

# Auto-download SDK/NDK (leave empty for GitHub Actions)
android.sdk_path =
android.ndk_path =

# Buildozer should create standalone APK
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.gradle_dependencies =
android.use_androidx = True

# --- iOS (optional, keep defaults) ---
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]

# Logging
log_level = 2
warn_on_root = 1
