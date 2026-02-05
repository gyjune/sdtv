FROM alpine:3.19

WORKDIR /app

# 安装Python和pip
RUN apk add --no-cache python3 py3-pip

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（添加详细输出以便调试）
RUN pip3 install --no-cache-dir -r requirements.txt --verbose

# 复制应用代码
COPY app.py .

EXPOSE 9002

CMD ["python3", "app.py"]