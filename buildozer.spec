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
requirements = python3,kivy,opencv
android.permissions = INTERNET

# --- Android Specific ---
android.archs = arm64-v8a, armeabi-v7a

# --- iOS (optional, keep defaults) ---
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
