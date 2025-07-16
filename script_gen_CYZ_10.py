import datetime # 匯入 Python 的時間函式庫

def generate_script(
    # Z 軸參數 (單位: mm)
    z_start, z_step, z_count,
    # Y 軸參數 (單位: mm)
    y_start, y_step, y_count,
    # 旋轉軸參數 (單位: 度)
    rotation_start, rotation_step, rotation_count,
    # 通用參數
    map_name, angle_res_interval, y_move_res_interval, output_filename
):
    """
    根據給定的參數生成自動化腳本，包含智慧等待邏輯。
    - 單位自動換算。
    - 等待邏輯: 根據下一個移動是 Z, Y, 還是旋轉軸來決定等待時間。
    """
    
    # --- 單位轉換係數 ---
    MM_TO_UM = 1000
    MM_TO_NM = 1000000
    DEG_TO_UDEG = 1000000
    
    script_content = []
    script_content.append("STR")
    script_content.append(f"DIR {map_name}")

    # 外層迴圈：控制 Z 軸 (SMV, ID=2)
    for i in range(z_count):
        current_z_mm = z_start + (i * z_step)
        output_z_um = current_z_mm * MM_TO_UM
        script_content.append(f"SMV,0,2,{int(output_z_um)}")

        # 中層迴圈：控制 Y 軸 (ID=1)
        for j in range(y_count):
            current_y_mm = y_start + (j * y_step)
            output_y_nm = current_y_mm * MM_TO_NM
            script_content.append(f"SMV,0,1,{int(output_y_nm)}")

            # 內層迴圈：在當前的 (Z, Y) 座標點上進行旋轉掃描 (FMV, ID=2)
            for k in range(rotation_count):
                current_rotation_deg = rotation_start + (k * rotation_step)
                output_rotation_udeg = current_rotation_deg * DEG_TO_UDEG
                script_content.append(f"FMV,0,2,{int(output_rotation_udeg)}")
                
                # 執行拍攝指令
                script_content.append("CAQ,4,0,1")

                # --- 智慧等待邏輯 ---
                is_last_rotation_step = (k == rotation_count - 1)
                is_last_y_step = (j == y_count - 1)

                # 情況一：接著是 Z 軸移動 (無等待)
                if is_last_rotation_step and is_last_y_step:
                    is_last_z_step = (i == z_count - 1)
                    if not is_last_z_step:
                        # 這是 Z 軸層的最後一次拍攝，且後面還有新的 Z 軸層，所以不等待
                        pass
                    else:
                        # 這是整個腳本的最後一次拍攝，按標準規則等待
                        script_content.append(f"RES,{angle_res_interval}")
                
                # 情況二：接著是 Y 軸移動 (短等待)
                elif is_last_rotation_step:
                    script_content.append(f"RES,{y_move_res_interval}")
                    
                # 情況三：接著是另一次旋轉 (標準等待)
                else:
                    script_content.append(f"RES,{angle_res_interval}")

    script_content.append("END")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(script_content))
        print(f"✅ 腳本已成功生成！\n   檔案儲存至: '{output_filename}'")
    except IOError as e:
        print(f"❌ 寫入檔案時發生錯誤: {e}")


# --- 參數設定 (請使用指定單位輸入) ---
# Z 軸設定 (單位: mm)
Z_AXIS_START = 4.3
Z_AXIS_STEP = 0.1
Z_AXIS_COUNT = 41

# Y 軸設定 (單位: mm)
Y_AXIS_START = 10
Y_AXIS_STEP = -0.1
Y_AXIS_COUNT = 41

# 旋轉軸設定 (單位: 度)
ROTATION_AXIS_START = 99.01
ROTATION_AXIS_STEP = 1
ROTATION_AXIS_COUNT = 1

# 通用設定
MAP_NAME = "Sample2_mosaic2"

# --- 可自訂的兩種 RES 等待時間 ---
# 規則 1 & 3: 標準等待 (僅旋轉後)
ANGLE_RES_INTERVAL = 69

# 規則 2: 較短等待 (旋轉結束，準備移動 Y 軸前)
Y_MOVE_RES_INTERVAL = 67


# --- 主程式執行 ---
if __name__ == "__main__":
    now = datetime.datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M%S")
    dynamic_filename = f"Script_{timestamp}.txt"

    generate_script(
        z_start=Z_AXIS_START, z_step=Z_AXIS_STEP, z_count=Z_AXIS_COUNT,
        y_start=Y_AXIS_START, y_step=Y_AXIS_STEP, y_count=Y_AXIS_COUNT,
        rotation_start=ROTATION_AXIS_START, rotation_step=ROTATION_AXIS_STEP, rotation_count=ROTATION_AXIS_COUNT,
        map_name=MAP_NAME,
        angle_res_interval=ANGLE_RES_INTERVAL,
        y_move_res_interval=Y_MOVE_RES_INTERVAL,
        output_filename=dynamic_filename
    )