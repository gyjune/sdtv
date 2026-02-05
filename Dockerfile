# 两阶段构建，最终镜像约15MB
FROM alpine:3.19 AS builder

WORKDIR /app

# 安装构建工具
RUN apk add --no-cache python3 py3-pip

COPY requirements.txt .

# 安装依赖到packages目录
RUN pip3 install --no-cache-dir -r requirements.txt -t /app/packages

# 最终镜像
FROM alpine:3.19

WORKDIR /app

# 只安装python3
RUN apk add --no-cache python3

# 从构建阶段复制依赖
COPY --from=builder /app/packages /usr/local/lib/python3.10/site-packages/

# 复制应用
COPY app.py .

EXPOSE 9002

CMD ["python", "app.py"]