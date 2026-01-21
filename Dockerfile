# 使用多架构基础镜像
FROM --platform=$BUILDPLATFORM python:3.10-slim AS builder

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖 - 使用-t参数指定安装目录
RUN pip install --no-cache-dir -r requirements.txt -t /app/packages

# 复制应用代码
COPY app.py .

# 最终阶段
FROM python:3.10-slim

WORKDIR /app

# 安装curl用于健康检查
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制已安装的包
# 注意：Python 3.10的site-packages路径是/usr/local/lib/python3.10/site-packages/
COPY --from=builder /app/packages /usr/local/lib/python3.10/site-packages/
COPY --from=builder /app/app.py .

EXPOSE 9002

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9002/ || exit 1

CMD ["python", "app.py"]