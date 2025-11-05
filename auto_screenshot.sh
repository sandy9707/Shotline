#!/bin/bash
# ~/scripts/auto_shottr_capture.sh
# 自动截图（Shottr URL Scheme）+ 自动压缩（ImageMagick mogrify）

output_root="/Volumes/lev/doclev/Screenshots"
output_dir="$output_root/$(date +%Y-%m-%d)"
mkdir -p "$output_dir"

# 获取当前活动应用，稍后恢复焦点
# current_app=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true')

for i in {1..3}; do
    # 调用 Shottr 截全屏
    open -g "shottr://grab/fullscreen?then=save"

    # 等待文件生成
    sleep 2

    # 找到最新截图文件
    latest=$(ls -t "$output_root" | grep '^SCR' | head -n 1)
    if [ -n "$latest" ]; then
        # 移动并重命名
        new_file="$output_dir/$(date +%H-%M-%S)_$i.png"
        mv "$output_root/$latest" "$new_file"

        # 使用 mogrify 压缩（覆盖原图）
        magick convert "$new_file" -quality 50 "${new_file%.*}.jpg" && rm "$new_file"

        echo "✅ 已保存并压缩: $new_file"
    fi

    # 恢复原应用焦点（减少前台闪烁）
    # osascript -e "tell application \"$current_app\" to activate"

    # 间隔 15 秒
    sleep 15
done
