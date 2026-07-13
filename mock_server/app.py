"""
Mock server cho môi trường LOCALHOST.

Mục đích: dựng một website đăng ký giả để test bot Playwright end-to-end
mà không đụng tới hệ thống thật. Server này cung cấp:

  GET  /register     -> Giao diện form nhập liệu (đúng các selector bot cần)
  GET  /captcha.png  -> Ảnh captcha (vẽ bằng Pillow)
  POST /register     -> Xử lý submit (bước 1: captcha, bước 2: OTP)
  POST /solve        -> Mock API giải captcha (Image-to-Text)
  GET  /receive      -> Mock API nhận OTP bên thứ ba

Chạy:  py mock_server/app.py
"""
import io
import random
import string

from flask import Flask, request, jsonify, Response
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Trạng thái tạm cho demo (chạy tuần tự từng account nên global là đủ)
STATE = {
    "captcha": "",      # captcha đang hiển thị
    "otps": {},         # email -> mã otp đã cấp
}


def _rand_code(n=5):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


# ----------------------- Giao diện & flow đăng ký -----------------------
PAGE_CSS = """
<style>
  body{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;
       display:flex;justify-content:center;padding:40px}
  .card{background:#1e293b;padding:32px;border-radius:14px;width:360px;
        box-shadow:0 10px 40px rgba(0,0,0,.4)}
  h2{margin:0 0 18px;text-align:center}
  label{display:block;font-size:13px;margin:12px 0 4px;color:#94a3b8}
  input{width:100%;padding:10px;border-radius:8px;border:1px solid #334155;
        background:#0f172a;color:#e2e8f0;box-sizing:border-box}
  img.captcha{margin-top:14px;border-radius:8px;display:block}
  button{width:100%;margin-top:20px;padding:12px;border:0;border-radius:8px;
         background:#3b82f6;color:#fff;font-size:15px;cursor:pointer}
  .success-message{background:#065f46;color:#d1fae5;padding:16px;border-radius:10px;
                   text-align:center;font-size:16px}
  .error-message{background:#7f1d1d;color:#fecaca;padding:10px;border-radius:8px;
                 margin-top:12px;text-align:center}
</style>
"""


@app.get("/")
def home():
    """Trang chu website - co nut mo form dang ky (dung luong that)."""
    return f"""
    {PAGE_CSS}
    <div class="card">
      <h2>MyWebsite</h2>
      <p style="text-align:center;color:#94a3b8">Chao mung den voi trang demo</p>
      <a id="open-register" href="/register">
        <button type="button">Dang ky tai khoan</button>
      </a>
    </div>
    """


@app.get("/register")
def register_form():
    STATE["captcha"] = _rand_code()
    return f"""
    {PAGE_CSS}
    <div class="card">
      <h2>Dang ky tai khoan</h2>
      <form method="POST" action="/register">
        <label>Tên đăng nhập</label>
        <input name="username" required>
        <label>Email</label>
        <input name="email" type="email" required>
        <label>Mật khẩu</label>
        <input name="password" type="password" required>
        <label>Họ và tên</label>
        <input name="full_name">
        <label>Nhập mã captcha bên dưới</label>
        <img class="captcha" src="/captcha.png?r={random.random()}" width="160" height="60">
        <input name="captcha" placeholder="Mã captcha" required>
        <button type="submit">Đăng ký</button>
      </form>
    </div>
    """


@app.get("/captcha.png")
def captcha_png():
    code = STATE["captcha"] or _rand_code()
    img = Image.new("RGB", (160, 60), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        font = ImageFont.load_default()
    draw.text((18, 12), code, fill=(147, 197, 253), font=font)
    # vài đường nhiễu cho giống captcha thật
    for _ in range(6):
        draw.line(
            [(random.randint(0, 160), random.randint(0, 60)),
             (random.randint(0, 160), random.randint(0, 60))],
            fill=(71, 85, 105), width=1,
        )
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return Response(buf.getvalue(), mimetype="image/png")


@app.post("/register")
def register_submit():
    otp = (request.form.get("otp") or "").strip()

    # ----- Bước 2: đã có OTP -----
    if otp:
        email = request.form.get("email", "")
        if otp == STATE["otps"].get(email):
            return f"""{PAGE_CSS}<div class="card">
                <div class="success-message">Dang ky thanh cong!<br>{email}</div></div>"""
        return _otp_page(email, error="Mã OTP không đúng")

    # ----- Bước 1: kiểm tra captcha -----
    email = request.form.get("email", "")
    captcha = (request.form.get("captcha") or "").strip().upper()
    if captcha != STATE["captcha"]:
        return f"""{PAGE_CSS}<div class="card"><h2>📝 Đăng ký tài khoản</h2>
            <div class="error-message">Captcha sai (nhập: {captcha or '—'})</div></div>""", 400

    # captcha đúng -> cấp OTP và hiển thị màn nhập OTP
    code = "".join(random.choices(string.digits, k=6))
    STATE["otps"][email] = code
    print(f"[MOCK] OTP cho {email}: {code}", flush=True)
    return _otp_page(email)


def _otp_page(email, error=""):
    err_html = f'<div class="error-message">{error}</div>' if error else ""
    return f"""
    {PAGE_CSS}
    <div class="card">
      <h2>Xac thuc OTP</h2>
      <p style="text-align:center;color:#94a3b8">Da gui ma toi {email}</p>
      {err_html}
      <form method="POST" action="/register">
        <input type="hidden" name="email" value="{email}">
        <label>Nhập mã OTP (6 số)</label>
        <input name="otp" required>
        <button type="submit">Xác nhận</button>
      </form>
    </div>
    """


# ----------------------- Mock API bên thứ ba -----------------------
@app.post("/solve")
def solve_captcha():
    """Mock 'Image-to-Text'. Ở đây trả thẳng captcha đang hiển thị."""
    return jsonify({"text": STATE["captcha"]})


@app.get("/receive")
def receive_otp():
    """Mock API nhận OTP theo email."""
    email = request.args.get("email", "")
    return jsonify({"otp": STATE["otps"].get(email)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
