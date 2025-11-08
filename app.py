import streamlit as st
from PIL import Image
import pandas as pd

uploaded_img = st.file_uploader("🖼️ 上傳圖片", type=["png","jpg","jpeg"])
uploaded_csv = st.file_uploader("📤 上傳 CSV", type=["csv"])

# 圖片處理
if uploaded_img:
    image = Image.open(uploaded_img)
else:
    image = None

# CSV 處理
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
else:
    df = pd.DataFrame({"x": range(10), "y": range(10)})

# 用 HTML + GridStack 放三個卡片
import streamlit.components.v1 as components

img_html = '<div style="text-align:center;color:gray;">尚未上傳圖片</div>'
if image:
    import io, base64
    buf = io.BytesIO()
    image.save(buf, format=image.format)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    img_html = f'<img src="data:image/{image.format.lower()};base64,{img_b64}" style="width:100%; height:auto;" />'

# 在 HTML 裡放置 img_html
components_html = f"""
<link rel="stylesheet" href="https://unpkg.com/gridstack@9.3.0/dist/gridstack.min.css"/>
<script src="https://unpkg.com/gridstack@9.3.0/dist/gridstack-all.js"></script>

<div class="grid-stack" style="min-height:80vh;">
  <div class="grid-stack-item" gs-w="4" gs-h="3">
    <div class="grid-stack-item-content">
      <h4>🖼️ 圖片</h4>
      {img_html}
    </div>
  </div>
</div>

<script>
const grid = GridStack.init({{float:true}});
</script>
"""

components.html(components_html, height=600, scrolling=True)
