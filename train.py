import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import umap
import json

# 1. 加载模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-zh")
model = AutoModel.from_pretrained("BAAI/bge-large-zh").to(device)
model.eval()

# 2. 文本嵌入函数
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0, :]  # [CLS] embedding
    return embeddings.squeeze().cpu().numpy()

# 3. 读取 CSV 文件（请改为你自己的文件路径）
df = pd.read_csv("bilibili_hot_videos_20250608.csv")  # 请替换为真实 CSV 文件路径

# ✅ 填充空值（将 NaN 替换为空字符串）
text_columns = ["标题", "描述", "点赞数", "评论数", "收藏数", "UP主昵称", "视频链接", "分类", "三级分类", "封面图片"]
for col in text_columns:
    if col in df.columns:
        if df[col].dtype == 'O':  # 如果是对象类型（字符串）
            df[col] = df[col].fillna("")
        else:
            # 对于数值列可以填 0 或其他默认值
            df[col] = df[col].fillna(0)

# 检查字段是否存在
required_cols = ["标题", "描述", "点赞数", "评论数", "收藏数", "UP主昵称", "视频链接", "分类", "三级分类", "封面图片"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"缺少字段：{col}")

# 4. 生成文本嵌入
print("正在生成文本嵌入...")
texts = (df["标题"].astype(str) + "。" + df["描述"].astype(str)).tolist()
embeddings = [get_embedding(text) for text in texts]

# 5. UMAP降维
print("正在降维处理...")
umap_model = umap.UMAP(n_components=3, random_state=42)
X_3d = umap_model.fit_transform(embeddings)

# 6. 组装为 JSON 格式
print("正在生成 JSON 数据...")
result = []
for idx, row in df.iterrows():
    item = {
        "id": int(idx),
        "title": str(row["标题"]) if pd.notna(row["标题"]) else "",
        "description": str(row["描述"]) if pd.notna(row["描述"]) else "",
        "position": X_3d[idx].tolist(),
        "点赞数": int(row["点赞数"]) if pd.notna(row["点赞数"]) else 0,
        "评论数": int(row["评论数"]) if pd.notna(row["评论数"]) else 0,
        "收藏数": int(row["收藏数"]) if pd.notna(row["收藏数"]) else 0,
        "UP主": str(row["UP主昵称"]) if pd.notna(row["UP主昵称"]) else "",
        "视频链接": str(row["视频链接"]) if pd.notna(row["视频链接"]) else "",
        "封面图片": str(row["封面图片"]) if pd.notna(row["封面图片"]) else "",
        "分类": str(row["分类"]) if pd.notna(row["分类"]) else "",
        "子分类": str(row["三级分类"]) if pd.notna(row["三级分类"]) else ""
    }
    result.append(item)

# 7. 写入 JSON 文件
output_path = "bilibili_video_embeddings.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成：{output_path}")