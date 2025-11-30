#!/bin/bash
# ~/scripts/auto_capture_unified.sh
# 统一截图脚本：支持 screencapture (原生直出) / osascript (模拟按键) / shottr (旧版)

# ================= 配置区域 =================
# 1. 设置截图模式: "screencapture" | "osascript" | "shottr"
screencapture_tool="screencapture"

# 2. 路径配置
output_root="/Volumes/lev/doclev/Screenshots"
downloads="/Volumes/lev/users/lev/Downloads"

# ===========================================

output_dir="$output_root/$(date +%Y-%m-%d)"
mkdir -p "$output_dir"

for i in {1..2}; do
    timestamp=$(date +%H-%M-%S)
    target_png="$output_dir/${timestamp}_${i}.png"
    target_jpg="$output_dir/${timestamp}_${i}.jpg"

    echo "📸 [模式: $screencapture_tool] 开始截图 $i/2 ..."

    # ================= 分支处理逻辑 =================
    case "$screencapture_tool" in
        "screencapture")
            # --- 模式 A: 系统原生命令 (最快，无需中转) ---
            # -x: 静音 (可选)
            # -m: 如果有多个屏幕，将捕获主屏幕 (或根据需求调整参数)
            screencapture -x "$target_png"
            ;;

        "osascript"|"shottr")
            # --- 模式 B: 模拟按键或 Shottr (依赖 Downloads 中转) ---

            # 1. 清理旧文件
            rm -f "$downloads"/Screenshot*.png

            # 2. 触发截图动作
            if [ "$screencapture_tool" == "osascript" ]; then
                # 模拟 Cmd+Shift+Opt+Ctrl+E (或者你自定义的快捷键)
                osascript -e 'tell application "System Events" to keystroke "e" using {command down, shift down, option down, control down}'
            elif [ "$screencapture_tool" == "shottr" ]; then
                # Shottr 备用分支
                open -g "shottr://grab/fullscreen?then=save"
            fi

            # 3. 等待文件生成 (根据你的经验值设为 10s)
            sleep 10

            # 4. 从 Downloads 捞取文件 (保留你原有的双屏处理逻辑)
            first=$(ls -t "$downloads" | grep '^Screenshot' | grep -v '(2)' | head -n 1)
            second=$(ls -t "$downloads" | grep '^Screenshot' | grep '(2)' | head -n 1)

            # 处理主截图
            if [ -n "$first" ]; then
                mv "$downloads/$first" "$target_png"
            else
                echo "⚠️ 未在 Downloads 找到截图文件"
            fi

            # 清理副屏截图 (如果存在)
            if [ -n "$second" ]; then
                rm -- "$downloads/$second"
            fi
            ;;
    esac

    # ================= 统一压缩处理 =================
    # 只要目标 PNG 存在，就执行压缩
    if [ -f "$target_png" ]; then
        magick "$target_png" -quality 50 "$target_jpg" && rm "$target_png"
        echo "✅ 已保存并压缩: $target_jpg"
    else
        echo "❌ 截图失败或文件未生成: $target_png"
    fi

    # ================= 循环等待 =================
    if [ "$i" -lt 2 ]; then
        echo "⏳ 等待 158 秒..."
        sleep 158
    fi
done