import os
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header

SENDER_EMAIL = os.environ.get("GMAIL_USER", "Fengzd3@gmail.com")
APP_PASSWORD = os.environ.get("GMAIL_PASS")
SUBJECT = "Request for Wholesale Catalog & Availability List (For Metro Vancouver Project)"

def load_suppliers():
    try:
        with open("suppliers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取 suppliers.json 失败: {e}")
        return []

def load_template():
    try:
        with open("email_template.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ 读取 email_template.txt 失败: {e}")
        return ""

def send_all_emails():
    suppliers = load_suppliers()
    template_content = load_template()

    if not suppliers or not template_content:
        print("❌ 配置文件缺失。")
        return
    if not APP_PASSWORD:
        print("❌ 错误：未找到 GMAIL_PASS 密码，请确保配置了 GitHub Secrets。")
        return

    try:
        print("正在连接 Gmail SMTP 服务器...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        print("🎉 Gmail 登录成功！开始组装并发送邮件...\n")

        for s in suppliers:
            company = s.get("company_name", "Sales Team")
            to_email = s.get("email")
            if not to_email:
                continue

            personalized_body = template_content.replace("{company_name}", company)
            message = MIMEText(personalized_body, 'plain', 'utf-8')
            message['From'] = Header(f"Zongde Feng <{SENDER_EMAIL}>", 'utf-8')
            message['To'] = Header(to_email, 'utf-8')
            message['Subject'] = Header(SUBJECT, 'utf-8')

            print(f"正在发送给: {company} <{to_email}> ...")
            server.sendmail(SENDER_EMAIL, [to_email], message.as_string())
            print(f"✅ 成功发送至: {to_email}")

        server.quit()
        print("\n🏁 所有邮件发送完毕！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    send_all_emails()
