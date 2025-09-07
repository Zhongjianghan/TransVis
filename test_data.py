import requests
import datetime
import time

def send_event(session_id, screen_id):
    """发送一个事件到后端"""
    data = {
        "session_id": session_id,
        "screen_id": screen_id,
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        response = requests.post("http://127.0.0.1:8000/track", json=data)
        if response.status_code == 200:
            print(f"成功发送事件: {session_id} -> {screen_id}")
        else:
            print(f"发送失败: {response.status_code}")
    except Exception as e:
        print(f"发送失败: {str(e)}")

def simulate_user_journey():
    """模拟用户访问journey"""
    # 用户A的访问路径：首页 -> 产品列表 -> 产品详情 -> 购物车
    send_event("userA", "首页")
    time.sleep(1)
    send_event("userA", "产品列表")
    time.sleep(1)
    send_event("userA", "产品详情")
    time.sleep(1)
    send_event("userA", "购物车")

    # 用户B的访问路径：首页 -> 搜索 -> 产品详情 -> 购物车
    send_event("userB", "首页")
    time.sleep(1)
    send_event("userB", "搜索")
    time.sleep(1)
    send_event("userB", "产品详情")
    time.sleep(1)
    send_event("userB", "购物车")

if __name__ == "__main__":
    print("开始模拟用户访问...")
    simulate_user_journey()
    print("模拟完成！")
