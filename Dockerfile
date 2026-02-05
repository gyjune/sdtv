# 使用多阶段构建减小镜像体积
FROM python:3.11-alpine as builder

WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache gcc musl-dev linux-headers

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 最终阶段
FROM python:3.11-alpine

WORKDIR /app

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/requirements.txt .

# 复制应用文件
COPY app.py .

# 确保pip安装的包在PATH中
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH

# 创建非root用户
RUN adduser -D -u 1000 sdtv && \
    chown -R sdtv:sdtv /app

USER sdtv

# 暴露端口
EXPOSE 9002

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:9002/ || exit 1

# 启动应用
CMD ["python", "app.py"]