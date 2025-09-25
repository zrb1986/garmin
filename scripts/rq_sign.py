# scripts/rq_sign.py
import httpx
import random
import time
import argparse

class RQAutoSign:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.base_url = "https://api.runningquotient.cn"
        self.client = httpx.Client(timeout=10)

    def login(self):
        url = f"{self.base_url}/api/v1/auth/login"
        payload = {"email": self.email, "password": self.password}
        r = self.client.post(url, json=payload)
        data = r.json()
        if "access_token" in data:
            print("✅ 登录成功")
            return data["access_token"], data["user"]["id"]
        else:
            raise Exception(f"登录失败: {data}")

    def sign(self, token, user_id):
        session_url = "https://runningquotient.cn/api/v1/dailySignIn"
        res = self.client.get(session_url)
        phpsessid = res.cookies.get("PHPSESSID")
        if not phpsessid:
            raise Exception("获取 PHPSESSID 失败")
        ts = int(time.time() * 1000)
        rnd = round(random.uniform(0, 2), 6)
        sign_url = f"{self.base_url}/api/v1/dailySignIn?_= {ts}{rnd}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Cookie": f"PHPSESSID={phpsessid}"
        }
        r = self.client.get(sign_url, headers=headers)
        data = r.json()
        if data.get("status") == "ok":
            print("🎉 签到成功！")
        else:
            print("❌ 签到失败：", data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="RQ 邮箱")
    parser.add_argument("--password", required=True, help="RQ 密码")
    args = parser.parse_args()
    rq = RQAutoSign(args.email, args.password)
    try:
        token, user_id = rq.login()
        rq.sign(token, user_id)
    except Exception as e:
        print("出错了：", e)
