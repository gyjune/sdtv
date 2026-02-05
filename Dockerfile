# 使用多阶段构建减小镜像体积
FROM python:3.11-alpine as builder

WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache gcc musl-dev linux-headers

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖到特定目录
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# 最终阶段
FROM python:3.11-alpine

WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /app/deps /app/deps

# 复制应用文件
COPY app.py .
COPY requirements.txt .

# 将依赖目录添加到Python路径
ENV PYTHONPATH=/app/deps:$PYTHONPATH
ENV PATH=/app/deps/bin:$PATH

# 创建非root用户
RUN adduser -D -u 1000 sdtv && \
    chown -R sdtv:sdtv /app

USER sdtv

# 暴露端口
EXPOSE 9002

# 启动应用
CMD ["python", "app.py"]