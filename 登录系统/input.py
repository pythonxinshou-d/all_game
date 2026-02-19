
"""
登录系统与小恐龙跳一跳游戏
========================

该模块实现了一个完整的用户登录注册系统以及一个基于pygame的小恐龙跳一跳游戏。

主要功能:
    1. 用户注册:支持用户名和6位数字密码的注册
    2. 用户登录:支持密码验证、密码找回、防暴力破解
    3. 数据加密:使用质数乘积算法对密码进行简单加密
    4. 游戏功能:小恐龙跳一跳，包含障碍物躲避、积分系统、排行榜

文件说明：
    - User_information.txt:存储用户信息（用户名和加密密码）
    - User_sort.txt:存储玩家排名信息（排名、用户名、分数）

作者:孙宇昂
创建日期:2026/2/17
"""
import json
import os
import time
import pygame as py
import random
# ==================== 全局变量与常量定义 ====================
# 用于密码加密的质数列表，每个数字(0-9)对应一个质数
# 选择较大的质数以增加加密强度，避免简单的逆向破解
prime_nums = [
    53231,
    53233,
    53611,
    53617,
    53623,
    53629,
    53791,
    53813,
    54013,
    54037,
    54049,
]

# 小写字母列表，用于用户名首字母验证和用户信息索引
# 用户信息按首字母分26组存储，提高查找效率
Letters = [chr(ord("a") + i) for i in range(26)]

# 数字字符列表，用于密码格式验证
nums = [str(i) for i in range(10)]

# 黄金分割比常量 (φ ≈ 0.618)
# 用于游戏界面布局中的美学比例计算
GOLDEN_RATIO = (5 ** 0.5 - 1) / 2


# ==================== 密码加密模块 ====================

def encrypt_password(password):
    """
    密码加密函数
    
    使用质数乘积算法对6位数字密码进行加密。
    
    加密原理：
        对于密码中的每一位数字d_i(位置从1开始),计算:
            prime_nums[d_i]*prime_nums[位置]+密码整体数值
        将所有位的计算结果累加得到最终加密值.
    
    设计思路:
        1.使用质数乘积增加破解难度
        2. 加入位置因子，使得相同数字在不同位置产生不同贡献
        3. 加入密码整体数值作为偏移量，进一步混淆

    参数：
        password (str): 待加密的密码,必须是6位数字字符串

    返回：
        int: 加密后的密码数值
        
    注意：
        - 此加密方法仅为教学演示，不应用于生产环境
        - 生产环境应使用bcrypt、Argon2等专业密码哈希算法
        - 加密后的值可能非常大,但Python支持大整数运算
    """
    Password_Storage = 0
    digit = 0
    password_int = int(password)
    
    # 逐位处理密码
    for i in password:
        digit += 1
        i = int(i)
        # 核心加密公式：质数乘积 + 密码整体值
        Password_Storage += prime_nums[i] * prime_nums[digit] + password_int
    
    return Password_Storage


# ==================== 数据文件检查模块 ====================

def Check(file_path: str, Correct_mistakes_content, light: bool):
    """
    用户数据文件检查与恢复函数
    
    功能描述：
        检查指定的数据文件是否存在、格式是否正确。
        如果文件不存在或格式损坏，使用默认内容重置。

    参数：
        file_path (str): 数据文件的路径（相对或绝对路径）
        Correct_mistakes_content (any): 当文件损坏或不存在时使用的默认内容
            - 对于User_information.txt: 应为26个空列表组成的列表 [[], [], ...]
            - 对于User_sort.txt: 应为空列表 []
        light (bool): 是否启用轻量级模式
            - True: 返回 (User_information, if_mistake) 元组，包含错误标记
            - False: 仅返回 User_information

    返回：
        当 light=True 时：
            tuple: (User_information, if_mistake)
                - User_information: 从文件读取的或默认的用户数据
                - if_mistake (bool): 是否发生了错误（文件不存在或格式损坏）
        当 light=False 时：
            any: 从文件读取的或默认的用户数据

    异常处理：
        - json.JSONDecodeError: 文件格式不是有效的JSON,使用默认内容重置
        - 文件不存在: 静默创建默认内容(light=True时会提示用户)

    使用场景：
        - 在读取用户信息前调用，确保数据文件可用
        - 自动修复损坏的数据文件
    """
    if_mistake = False
    User_information = Correct_mistakes_content
    
    try:
        # 检查文件是否存在
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                # 文件非空时解析JSON
                if content:
                    User_information = json.loads(content)
                    if_mistake = False
                else:
                    # 文件为空，使用默认内容
                    User_information = Correct_mistakes_content
        else:
            # 文件不存在
            if light:
                print("暂无用户注册，将为你跳转注册流程！")
                if_mistake = True
            User_information = Correct_mistakes_content
    
    except json.JSONDecodeError:
        # JSON解析失败，文件格式损坏
        if light:
            print("用户数据文件损坏，已重置！请重新注册。")
            if_mistake = True
        else:
            print("用户数据文件格式损坏，已自动重置！")
        User_information = Correct_mistakes_content
    
    # 根据light参数返回不同格式
    if light:
        return User_information, if_mistake
    else:
        return User_information


# ==================== 用户注册模块 ====================

def Registration():
    """
    用户注册信息输入与验证函数
    
    功能描述：
        通过命令行交互获取用户输入的用户名和密码，并进行格式验证。
        验证失败时提示用户重新输入，直到输入符合要求。

    用户名规则：
        1. 不能为空
        2. 首字符必须是小写字母(a-z)
        3. 长度不超过15个字符

    密码规则：
        1. 必须是6位数字
        2. 不能包含字母或特殊字符

    参数：
        无

    返回：
        tuple: (Username, Password_Initial)
            - Username (str): 验证通过的用户名
            - Password_Initial (str): 验证通过的原始密码（未加密）

    设计思路：
        使用while循环持续验证输入,直到输入有效为止,确保数据格式正确性.

    使用场景:
        - 新用户注册时调用
        - 密码找回时重新设置密码时调用
    """
    # 用户名输入与验证
    while True:
        Username = input("输入用户名,首位为小写字母,15位以内:")
        
        # 检查是否为空
        if not Username:
            print("用户名不能为空，请重新输入！")
            continue
        
        # 检查首字符和长度
        if len(Username) > 15 or Username[0] not in Letters:
            print("用户名格式错误(首位小写字母、15位以内)!")
            continue
        
        break

    # 密码输入与验证
    while True:
        Password_Initial = input("输入六位数字密码：")
        
        # 检查是否为6位数字
        if len(Password_Initial) != 6 or not Password_Initial.isdigit():
            print("密码格式错误!必须是6位数字)!")
            continue
        
        break
    
    return Username, Password_Initial


def Storage(Username: str, Password_Initial: str):
    """
    用户信息存储函数
    
    功能描述:
        将用户注册信息加密后存储到文件中,同时初始化玩家排名记录。
        自动检查用户名是否已存在,避免重复注册.

    数据存储结构:
        User_information.txt:
            [
                [ [用户名1, 加密密码1], [用户名2, 加密密码2], ... ],  # a开头的用户
                [ ... ],  # b开头的用户
                ...
                [ ... ]   # z开头的用户
            ]
            共26个子列表,对应26个小写字母

        User_sort.txt:
            [
                [排名1, 用户名1, 分数1],
                [排名2, 用户名2, 分数2],
                ...
            ]

    参数：
        Username (str): 要注册的用户名（已通过格式验证）
        Password_Initial (str): 原始密码(未加密的6位数字)

    返回：
        list: 更新后的用户信息列表(User_information)

    关键逻辑:
        1. 根据用户名首字母确定存储索引
        2. 检查该字母分组中是否已存在相同用户名
        3. 如存在，要求用户重新输入
        4. 如不存在，将新用户信息添加到对应分组
        5. 同时在排名文件中添加新玩家记录

    异常处理：
        - 用户名已存在：触发重新输入流程
        - 文件写入失败:由Python底层抛出异常(未显式处理)
    """
    # 加密密码
    Password_Storage = encrypt_password(Password_Initial)

    # 读取或初始化用户信息文件
    file_path = "User_information.txt"
    User_information = Check(file_path, [[] for _ in range(26)], False)

    # 检查用户名是否已存在
    while True:
        username_exists = False
        # 根据首字母找到对应的分组索引
        idx = Letters.index(Username[0])
        
        # 遍历该分组检查是否有重复用户名
        for j in User_information[idx]:
            if Username == j[0]:
                print("该用户名已存在请重新输入")
                # 用户名已存在，重新获取注册信息
                Username, Password_Initial = Registration()
                Password_Storage = encrypt_password(Password_Initial)
                username_exists = True
                break
        
        # 用户名不存在，退出检查循环
        if not username_exists:
            break

    # 添加新用户信息到对应分组
    User_information[idx].append([Username, Password_Storage])
    
    # 写入用户信息文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(User_information, f, ensure_ascii=False)

    # 读取或初始化排名文件
    file_path = "User_sort.txt"
    User_sort = Check(file_path, [], False)
    
    # 添加新玩家到排名（初始分数为0）
    User_sort.append([len(User_sort) + 1, Username, 0])
    
    # 写入排名文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(User_sort, f, ensure_ascii=False)

    print(f"注册成功！用户名 {Username} 已存储，密码已加密。")
    return User_information


def Register():
    """
    用户注册主函数
    
    功能描述：
        封装完整的注册流程，是外部调用注册功能的统一入口。

    执行流程：
        1. 调用Registration()获取并验证用户输入
        2. 调用Storage()存储用户信息

    参数：
        无

    返回：
        str: 注册成功的用户名

    使用场景：
        - 用户选择注册时调用
        - 密码找回失败时跳转注册
    """
    Username, Password_Initial = Registration()
    Storage(Username, Password_Initial)
    return Username


# ==================== 用户登录模块 ====================

def Login():
    """
    用户登录主函数
    
    功能描述：
        实现完整的用户登录流程，包括密码验证、密码找回、防暴力破解机制。

    核心功能：
        1. 用户名密码验证
        2. 密码找回功能（通过重新设置密码）
        3. 防暴力破解：
            - 第1-4次错误:仅提示重新输入
            - 第5次错误:暂停1分钟
            - 第10次错误:暂停2分钟
            - 第15次错误:暂停3分钟
            - 以此类推:暂停时间 = (错误次数 // 5) 分钟 

    防暴力破解策略：
        - 第1-4次错误:仅提示重新输入
        - 第5次错误:暂停1分钟
        - 第10次错误:暂停2分钟
        - 第15次错误:暂停3分钟
        - 以此类推:暂停时间 = (错误次数 // 5) 分钟

    密码找回流程：
        1. 用户输入"1"选择密码找回
        2. 输入用户名（需与原注册一致）和新密码
        3. 系统查找用户并更新密码
        4. 如用户不存在，跳转到注册流程

    参数：
        无

    返回：
        str: 登录成功的用户名

    异常处理：
        - IndexError: 用户数据格式异常，提示重新注册
        - 文件不存在或损坏:自动调用Check()处理

    关键变量说明：
        - light (bool):标记是否通过密码找回成功重置密码
        - times (int):记录连续输入错误的次数
    """
    light = False
    times = 0
    file_path = "User_information.txt"
    default_user_info = [[] for _ in range(26)]

    while True:
        times += 1

        # 防暴力破解：每5次错误暂停一段时间
        if times % 5 == 0:
            pause_min = times // 5
            pause_sec = pause_min * 60
            print(f"输错{times}次，暂停{pause_min}分钟后再试！")
            time.sleep(pause_sec)

        # 提供密码找回选项（从第2次错误开始）
        elif times > 1 and not light:
            Forget = input("如果忘记密码输入\"1\",否则按任意键继续登录：")
            if Forget == "1":
                print("输入新的密码完成密码找回（用户名需与原注册一致）")
                Username, Password_Initial = Registration()
                Password_Storage = encrypt_password(Password_Initial)

                # 检查用户数据文件
                User_information, if_mistake = Check(file_path, default_user_info, True)
                if if_mistake:
                    # 文件有问题，跳转到注册
                    Register()
                    break
                else:
                    user_found = False
                    idx = Letters.index(Username[0])
                    # 查找用户并更新密码
                    for k, (name, pwd) in enumerate(User_information[idx]):
                        if name == Username:
                            User_information[idx][k] = [Username, Password_Storage]
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(User_information, f, ensure_ascii=False)
                            user_found = True
                            light = True
                            print(f"用户{Username}密码找回成功！")
                            break
                    if not user_found:
                        # 用户未注册，跳转到注册
                        print("该用户未注册，将为你跳转注册流程！")
                        Register()
                        break

        # 密码找回成功，退出登录循环
        if light:
            break

        # 获取登录信息并验证
        Username, Password_Initial = Registration()
        Password_Storage = encrypt_password(Password_Initial)

        User_information = Check(file_path, default_user_info, False)
        login_success = False
        try:
            idx = Letters.index(Username[0])
            # 遍历对应用户名首字母的分组
            for name, pwd in User_information[idx]:
                if name == Username and pwd == Password_Storage:
                    print(f"用户{Username}登录成功！")
                    login_success = True
                    break
        except IndexError:
            # 用户数据格式异常
            print("用户数据格式异常，请重新注册！")
            Register()
            break

        # 登录成功，退出循环
        if login_success:
            break
        else:
            print("用户名或密码错误，请重新尝试！")
    
    return Username


# ==================== 主菜单与游戏模块 ====================

def ask():
    """
    主菜单与游戏主函数
    
    功能描述：
        程序的主入口函数，提供登录/注册选择菜单，以及游戏功能菜单。
        包含完整的小恐龙跳一跳游戏实现。

    菜单流程：
        1. 登录/注册选择
        2. 游戏主菜单：
           - 选项1:查看游戏规则
           - 选项2:查看排行榜
           - 选项3:开始游戏
           - 其他:退出程序

    游戏功能概述：
        - 玩家控制小恐龙躲避仙人掌和翼龙
        - 空格键跳跃，下箭头键趴下
        - 游戏时间越长，速度越快，障碍物越密集
        - 分数即为存活时间（秒）
        - 游戏结束后自动更新历史最高分数和排行榜

    游戏物理引擎：
        使用简化的抛物线运动模拟跳跃：
            height = v0 * t - 0.5 * g * t²
        其中v0为初速度,g为重力加速度

    参数：
        无

    返回：
        无

    性能优化：
        1. 图片预加载：游戏开始前加载所有图片资源
        2. convert()优化:使用pygame的convert()方法加速图片绘制
        3. 常量缓存：将频繁使用的计算结果缓存到变量
        4. 碰撞检测优化：使用缩小的碰撞矩形提高检测效率

    异常处理：
        - 图片加载失败：打印错误信息并返回
        - 字体加载失败：降级使用默认字体
    """
    # ==================== 登录/注册阶段 ====================
    while True:
        answer = input("你是要登录(输入1)还是要注册(输入2):")
        if answer == "1":
            Username = Login()
            break
        elif answer == "2":
            Username = Register()
            break
        else:
            print("输入错误,请输入1(登录)或2(注册):")
            continue

    # ==================== 游戏主菜单阶段 ====================
    while True:
        answer = input(
            "你是要查看游戏规则(输入1)或排名(输入2),还是要开始游戏(输入3),其余键退出:"
        )
        
        # 选项1：查看游戏规则
        if answer == "1":
            input(
                "           小恐龙跳一跳游戏\n    时间决定积分时间越长速度越快\n路上会随机刷新仙人掌,还需要躲避翼龙(飞行翼龙需要下蹲才能躲避)\n       空格键是跳跃下键为趴下\n分数即为坚持的时间时间越长速度越快怪物更密集\n            按任意键退出"
            )
        
        # 选项2：查看排行榜
        elif answer == "2":
            file_path = os.path.abspath("User_sort.txt")
            User_sort = Check(file_path, [], False)
            your_sort = "未参与游戏"
            your_grade = 0
            target_username = Username.strip()
            
            # 按分数降序排序
            sorted_user_sort = sorted(User_sort, key=lambda x: x[2], reverse=True) if User_sort else []
            User_sort_Front = sorted_user_sort[:10]  # 只显示前10名
            
            # 查找当前用户的排名
            for idx, info in enumerate(sorted_user_sort, 1):
                if info[1].strip() == target_username:
                    your_sort = idx
                    your_grade = info[2]
                    break
            
            # 格式化显示排名
            front_str = "\n".join([f"第{i+1}名: {info[1]} 分数:{info[2]}" for i, info in enumerate(User_sort_Front)]) if User_sort_Front else "排名为空,快来游玩吧"
            input(f"前10名排名:\n{front_str}\n你的排名为:{your_sort} | 你的分数:{your_grade}\n按任意键退出")
        
        # 选项3：开始游戏
        elif answer == "3":
            file_path = os.path.abspath("User_sort.txt")
            py.init()
            
            # ==================== 游戏常量与变量初始化 ====================
            
            Speed = 100  # 游戏初始速度（像素/秒）
            Speed_Increase = 50  # 每次速度增加量
            Speed_Increase_times = 0  # 速度增加次数计数
            jump_times = 0  # 跳跃次数（0=未开始，1=第一次跳跃即开始游戏）
            change_light = False  # 标记分数是否更新
            i = -1  # 当前用户在排名列表中的索引
            game_light = True  # 游戏主循环控制标志
            jump_light = False  # 跳跃状态标志
            down_light = False  # 趴下状态标志
            window_wide = 1204  # 窗口宽度（像素）
            window_height = 600  # 窗口高度（像素）
            
            # 小恐龙初始位置：使用黄金分割比确定水平位置
            Dinosaur_x = int(window_wide * (1 - GOLDEN_RATIO))
            Dinosaur_y = window_height / 2  # 小恐龙初始垂直位置
            
            g = 5  # 重力加速度（用于跳跃物理模拟）
            Dinosaur_jump = 40  # 跳跃初速度
            FPS = 60  # 游戏帧率（帧/秒）
            time_total = 0  # 游戏总时间（秒），同时也是分数
            clock = py.time.Clock()  # pygame时钟对象，用于控制帧率
            start_time = 0  # 游戏开始时间戳
            down_start_time = 0  # 趴下开始时间戳
            down_now_time = 0  # 趴下当前时间戳
            jump_start_time = 0  # 跳跃开始时间戳
            jump_now_time = 0  # 跳跃当前时间戳
            
            obstacles = []  # 障碍物列表，每个元素是一个字典
            distance_since_last_obstacle = 0  # 距离上一个障碍物生成的距离
            obstacle_min_distance = 300  # 障碍物之间的最小距离
            
            Background_x = 0  # 背景滚动偏移量
            Background_y = window_height / 2 + 45  # 地面Y坐标
            
            dead_dino_x = 0  # 死亡时小恐龙的X坐标
            dead_dino_y = 0  # 死亡时小恐龙的Y坐标
            was_jumping = False  # 标记死亡时是否在跳跃
            was_down = False  # 标记死亡时是否在趴下
            
            # ==================== 性能优化：预计算常量 ====================
            # 将频繁使用的计算结果缓存，避免在主循环中重复计算
            anim_duration_normal_0 = 1000 // FPS
            anim_duration_normal_1 = 2 * anim_duration_normal_0
            anim_duration_down = 2000 // FPS
            anim_duration_down_threshold = 1000 // FPS
            
            # ==================== 字体加载 ====================
            try:
                language = py.font.SysFont("SimSun", 20)
            except:
                # 加载失败时降级使用默认字体
                language = py.font.Font(None, 20)
                
            # ==================== 窗口初始化 ====================
            screen = py.display.set_mode((window_wide, window_height))
            py.display.set_caption("小恐龙跳一跳游戏")
            
            # ==================== 图片资源预加载 ====================
            # 性能优化：使用convert()和convert_alpha()加速绘制
            try:
                dinosaur = py.image.load("dinosaur.jpg").convert()
                dinosaur1 = py.image.load("dinosaur1.jpg").convert()
                dinosaur2 = py.image.load("dinosaur2.jpg").convert()
                dinosaur_down = py.image.load("dinosaur_down.jpg").convert()
                dinosaur_down1 = py.image.load("dinosaur_down1.png").convert_alpha()
                dinosaur_kill = py.image.load("dinosaur_kill.jpg").convert()
                fly_dinosaurs_up = py.image.load("dinosaur_fly_up.jpg").convert()
                fly_dinosaurs_down = py.image.load("dinosaur_fly_down.jpg").convert()
                big_Cactus = py.image.load("big_cactus.jpg").convert()
                small_Cactus = py.image.load("small_cactus.jpg").convert()
                Cloud = py.image.load("window.jpg").convert()
                
                # 缓存图片尺寸
                dinosaur_width = dinosaur.get_width()
                dinosaur_height = dinosaur.get_height()
                dinosaur_down_width = dinosaur_down.get_width()
                dinosaur_down_height = dinosaur_down.get_height()
            except Exception as e:
                print(f"图片加载失败: {e}")
                return

            # ==================== 游戏主循环 ====================
            while game_light:
                # 事件处理
                for event in py.event.get():
                    if event.type == py.QUIT:
                        game_light = False
                    elif event.type == py.KEYDOWN:
                        # 空格键：跳跃（不在跳跃或趴下状态时）
                        if event.key == py.K_SPACE and not jump_light and not down_light:
                            jump_times += 1
                            if jump_times != 1:
                                jump_light = True
                                jump_start_time = py.time.get_ticks()
                            # 第一次跳跃时记录游戏开始时间
                            if jump_times == 1:
                                start_time = py.time.get_ticks()
                        # 下箭头键：趴下（不在跳跃状态时）
                        elif event.key == py.K_DOWN and not jump_light:
                            down_light = True
                            down_start_time = py.time.get_ticks()
                            
                # 清屏（白色背景）
                screen.fill("white")
                
                # ==================== 游戏开始前的提示 ====================
                if jump_times == 0:
                    Font = language.render("按空格键开始游戏", True, (0, 0, 0))
                    screen.blit(Font, (window_wide / 2 - 80, window_height / 2 - 100))
                    
                # ==================== 游戏进行中 ====================
                if jump_times >= 1 and start_time > 0:
                    now_time = py.time.get_ticks()
                    
                    # 背景滚动
                    Background_x -= Speed / FPS
                    background_pattern_width = 900
                    # 背景图案循环
                    if Background_x < -background_pattern_width:
                        Background_x += background_pattern_width
                    
                    # 绘制地面和背景元素
                    if_rect_1 = Background_y - 6
                    if_rect_2 = Background_y + 1
                    py.draw.aaline(screen, (192, 192, 192), (0, Background_y), (window_wide, Background_y))
                    
                    # 绘制三组重复的背景图案
                    for i in range(3):
                        offset = i * background_pattern_width
                        # 绘制地面装饰矩形
                        py.draw.rect(screen, (192, 192, 192), (Background_x + offset, if_rect_1, 32, 18), 2, 7, 7, 7)
                        py.draw.rect(screen, (192, 192, 192), (Background_x + 300 + offset, if_rect_2, 8, 6), 1, 3, 3, 3)
                        # 绘制云朵
                        screen.blit(Cloud, (Background_x + 600 + offset, Background_y - 270))
                        
                    # 遮盖地面以下的区域
                    py.draw.rect(screen, (255, 255, 255), (0, Background_y + 1, window_wide, window_height))
                    
                    current_y = Dinosaur_y
                    
                    # ==================== 小恐龙状态处理 ====================
                    
                    # 状态1：跳跃中
                    if jump_light and jump_times != 1:
                        jump_now_time = now_time
                        jump_duration = (jump_now_time - jump_start_time) / 100
                        # 抛物线运动公式：h = v0*t - 0.5*g*t²
                        jump_height = Dinosaur_jump * jump_duration - 0.5 * g * (jump_duration ** 2)
                        current_y = Dinosaur_y - jump_height
                        # 落地检测
                        if jump_height <= 0:
                            jump_light = False
                            current_y = Dinosaur_y
                        screen.blit(dinosaur, (Dinosaur_x, current_y))
                    
                    # 状态2：趴下中
                    elif down_light:
                        down_now_time = now_time
                        down_duration = (down_now_time - down_start_time) / 1000
                        # 趴下持续1秒后自动站起
                        if down_duration >= 1:
                            down_light = False
                        # 趴下动画帧切换
                        anim_duration = (now_time - start_time) % anim_duration_down
                        if anim_duration < anim_duration_down_threshold:
                            screen.blit(dinosaur_down, (Dinosaur_x, Dinosaur_y + 13))
                        else:
                            screen.blit(dinosaur_down1, (Dinosaur_x + 1, Dinosaur_y - 3))
                    
                    # 状态3：正常跑动
                    else:
                        # 三帧跑动动画
                        anim_duration = (now_time - start_time) % (3000 // FPS)
                        if anim_duration < (1000 // FPS):
                            screen.blit(dinosaur, (Dinosaur_x, Dinosaur_y))
                        elif anim_duration < 2 * (1000 // FPS):
                            screen.blit(dinosaur1, (Dinosaur_x, Dinosaur_y))
                        else:
                            screen.blit(dinosaur2, (Dinosaur_x, Dinosaur_y))
                            
                    # ==================== 游戏时间与速度控制 ====================
                    time_total = (now_time - start_time) // 1000
                    
                    # 每15秒增加一次速度
                    if time_total % 15 == 0 and time_total > 0:
                        if time_total // 15 != Speed_Increase_times:
                            Speed += Speed_Increase
                            Speed_Increase_times += 1
                            
                    # ==================== 障碍物生成 ====================
                    distance_since_last_obstacle += Speed / FPS
                    
                    # 动态调整最大障碍物距离（时间越长，障碍物越密集）
                    obstacle_max_distance = 500 - time_total // 3 if time_total < 300 else 400
                    
                    # 在随机距离生成新障碍物
                    if distance_since_last_obstacle >= random.randint(obstacle_min_distance, obstacle_max_distance):
                        obstacle_type = random.choice(['fly_dinosaur', 'big_cactus', 'small_cactus'])
                        if obstacle_type == 'fly_dinosaur':
                            # 翼龙：飞行高度略低于小恐龙站立高度
                            y_pos = Dinosaur_y - 13
                            obstacles.append({'type': 'fly_dinosaur', 'x': window_wide, 'y': y_pos, 'anim_frame': 0, 'anim_time': 0})
                        elif obstacle_type == 'big_cactus':
                            # 大仙人掌
                            obstacles.append({'type': 'big_cactus', 'x': window_wide, 'y': Background_y - 45})
                        elif obstacle_type == 'small_cactus':
                            # 小仙人掌
                            obstacles.append({'type': 'small_cactus', 'x': window_wide, 'y': Background_y - 33})
                        distance_since_last_obstacle = 0
                        
                    # ==================== 障碍物更新与碰撞检测 ====================
                    new_obstacles = []
                    for obs in obstacles:
                        obs['x'] -= Speed / FPS
                        # 只保留屏幕内的障碍物
                        if obs['x'] > -200:
                            # 确定小恐龙当前的碰撞框
                            dinosaur_current_y = Dinosaur_y
                            current_dino_width = dinosaur_width
                            current_dino_height = dinosaur_height
                            
                            if jump_light and jump_times != 1:
                                dinosaur_current_y = current_y
                            elif down_light:
                                dinosaur_current_y = Dinosaur_y + 13
                                current_dino_height = dinosaur_down_height
                                
                            # 碰撞检测优化：使用70%大小的碰撞矩形，避免视觉上未碰撞却判定碰撞
                            if down_light:
                                dinosaur_rect = py.Rect(Dinosaur_x, dinosaur_current_y, current_dino_width, current_dino_height * 0.7)
                            else:
                                dinosaur_rect = py.Rect(Dinosaur_x, dinosaur_current_y, current_dino_width * 0.7, current_dino_height * 0.7)
                                
                            # 根据障碍物类型绘制并检测碰撞
                            if obs['type'] == 'fly_dinosaur':
                                # 翼龙动画
                                obs['anim_time'] += 16
                                if obs['anim_time'] > 200:
                                    obs['anim_frame'] = 1 - obs['anim_frame']
                                    obs['anim_time'] = 0
                                fly_img = fly_dinosaurs_up if obs['anim_frame'] == 0 else fly_dinosaurs_down
                                screen.blit(fly_img, (obs['x'], obs['y']))
                                obs_rect = py.Rect(obs['x'], obs['y']-window_height, fly_img.get_width() * 0.7, window_height+fly_img.get_height() * 0.7)
                            elif obs['type'] == 'big_cactus':
                                screen.blit(big_Cactus, (obs['x'], obs['y']))
                                obs_rect = py.Rect(obs['x'], obs['y'], big_Cactus.get_width() * 0.7, big_Cactus.get_height() * 0.7)
                            elif obs['type'] == 'small_cactus':
                                screen.blit(small_Cactus, (obs['x'], obs['y']))
                                obs_rect = py.Rect(obs['x'], obs['y'], small_Cactus.get_width() * 0.7, small_Cactus.get_height() * 0.7)
                                
                            # 碰撞检测
                            if dinosaur_rect.colliderect(obs_rect):
                                # 记录死亡时的位置和状态
                                dead_dino_x = Dinosaur_x
                                if jump_light and jump_times != 1:
                                    dead_dino_y = current_y
                                    was_jumping = True
                                    was_down = False
                                elif down_light:
                                    dead_dino_y = Dinosaur_y + 13
                                    was_jumping = False
                                    was_down = True
                                else:
                                    dead_dino_y = Dinosaur_y
                                    was_jumping = False
                                    was_down = False
                                game_light = False
                                
                            new_obstacles.append(obs)
                    obstacles = new_obstacles
                    
                # ==================== HUD显示（分数和速度） ====================
                Font = language.render(f"分数:{time_total}", True, (0, 0, 0))
                screen.blit(Font, (window_wide / 2 - 25, 0))
                Font = language.render(f"速度:{Speed}", True, (0, 0, 0))
                screen.blit(Font, (0, 0))
                py.display.update()
                clock.tick(FPS)
                
                # ==================== 游戏结束处理 ====================
                if not game_light:
                    # 绘制死亡画面
                    if down_light:
                        py.draw.rect(screen, (255, 255, 255), (Dinosaur_x, Dinosaur_y + 13, dinosaur_down_width*1.5, dinosaur_down_height * 0.7))
                        screen.blit(dinosaur_kill, (dead_dino_x, dead_dino_y - 13))
                    else:
                        screen.blit(dinosaur_kill, (dead_dino_x, dead_dino_y))
                    py.display.update()
                    py.time.wait(500)
                    
                    # 清屏并显示最终分数
                    screen.fill("white")
                    Font = language.render(f"本局分数:{time_total}", True, (0, 0, 0))
                    screen.blit(Font, (window_wide / 2 - 20, window_height / 2 - 10))
                    
                    # ==================== 更新玩家分数和排名 ====================
                    file_path = os.path.abspath("User_sort.txt")
                    User_sort = Check(file_path, [], False)
                    change_light = False
                    i = -1
                    target_username = Username.strip()
                    
                    # 查找当前用户并更新分数
                    for idx, (sort, name, grade) in enumerate(User_sort):
                        if name.strip() == target_username:
                            i = idx
                            if time_total > grade:
                                User_sort[i][2] = time_total
                                change_light = True
                            else:
                                # 未打破记录，显示历史最高分
                                time_total = grade
                            break
                    
                    # 如果分数更新，重新排序并保存
                    if change_light:
                        # 按分数降序排序
                        User_sort.sort(key=lambda x: x[2], reverse=True)
                        # 更新排名编号
                        for rank, info in enumerate(User_sort, 1):
                            info[0] = rank
                        # 保存到文件
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(User_sort, f, ensure_ascii=False)
                    
                    # 显示历史最高分
                    Font = language.render(f"你历史最高分数:{time_total}", True, (0, 0, 0))
                    screen.blit(Font, (window_wide / 2 - 75, window_height / 2 + 10))
                    Font = language.render(f"按叉号退出", True, (0, 0, 0))
                    screen.blit(Font, (window_wide / 2, window_height / 2 + 30))
                    py.display.update()
                    
                    # 等待用户关闭窗口
                    light = True
                    while light:
                        for event in py.event.get():
                            if event.type == py.QUIT:
                                light = False
                                break
            py.quit()
        
        # 其他输入：退出程序
        else:
            break


# ==================== 程序入口 ====================

if __name__ == "__main__":
    """
    程序入口
    
    当直接运行该脚本时,调用ask()函数启动程序.
    
    执行流程：
        1.显示登录/注册菜单
        2.用户登录或注册
        3.显示游戏主菜单
        4.根据用户选择执行相应功能
    """
    ask()

