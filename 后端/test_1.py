import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/users/login/"
PROTECTED_URL = f"{BASE_URL}/bot/chat/"  # 这个接口现在应该需要权限
PUBLIC_URL = f"{BASE_URL}/fitness/equipment/" # 这个接口应该是公开的

def run_test():
    print("="*30)
    print("🚀 开始 JWT 鉴权与业务逻辑测试")
    print("="*30)

    # ------------------------------------------------
    # 1. 测试公开接口 (无需 Token)
    # ------------------------------------------------
    print(f"\n[1] 测试公开接口: {PUBLIC_URL}")
    try:
        resp = requests.get(PUBLIC_URL)
        if resp.status_code == 200:
            print("    ✅ 公开接口访问成功！")
        else:
            print(f"    ❌ 公开接口失败: {resp.status_code}")
    except Exception as e:
        print(f"    ❌ 连接失败: {e}")
        return

    # ------------------------------------------------
    # 2. 测试受保护接口 (不带 Token -> 应该失败)
    # ------------------------------------------------
    print(f"\n[2] 测试无 Token 访问受保护接口: {PROTECTED_URL}")
    resp = requests.post(PROTECTED_URL, json={"message": "你好"})
    if resp.status_code == 401:
        print("    ✅ 鉴权拦截生效！(返回了 401 Unauthorized)")
    elif resp.status_code == 200:
        print("    ❌ 警告：接口未受保护，任何人都能访问！")
    else:
        print(f"    ❓ 其他状态码: {resp.status_code}")

    # ------------------------------------------------
    # 3. 测试登录 (获取 Token)
    # ------------------------------------------------
    print(f"\n[3] 模拟微信登录: {LOGIN_URL}")
    # 模拟发送 code
    payload = {"code": "mock_wechat_code_123"} 
    resp = requests.post(LOGIN_URL, json=payload)
    
    token = None
    if resp.status_code == 200:
        data = resp.json()
        if 'access' in data:
            token = data['access']
            print(f"    ✅ 登录成功！获取到 Token (前30字符): {token[:30]}...")
        else:
            print(f"    ❌ 登录返回格式不对: {data}")
            return
    else:
        print(f"    ❌ 登录失败: {resp.status_code} - {resp.text}")
        return

    # ------------------------------------------------
    # 4. 测试受保护接口 (带 Token -> 应该成功)
    # ------------------------------------------------
    print(f"\n[4] 使用 Token 访问受保护接口...")
    # 在 Header 中添加 Authorization: Bearer <token>
    headers = {
        "Authorization": f"Bearer {token}"
    }
    chat_payload = {"message": "怎么练胸？", "user_id": data.get('user_id', 1)}
    
    resp = requests.post(PROTECTED_URL, json=chat_payload, headers=headers)
    
    if resp.status_code == 200:
        print("    ✅ 鉴权通过！接口访问成功。")
        print(f"    🤖 AI回复: {resp.json()}")
    else:
        print(f"    ❌ 访问失败: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    run_test()