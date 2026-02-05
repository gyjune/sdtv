# 使用多阶段构建 - 简化版（因为不需要编译工具）
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt -t /app/packages

# 复制应用代码
COPY app.py .

# 最终阶段
FROM python:3.10-alpine

WORKDIR /app

# 安装curl用于健康检查（Alpine中包名不同）
RUN apk add --no-cache curl

# 从builder阶段复制已安装的包
COPY --from=builder /app/packages /usr/local/lib/python3.10/site-packages/
COPY --from=builder /app/app.py .

EXPOSE 9002

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9002/ || exit 1

CMD ["python", "app.py"]