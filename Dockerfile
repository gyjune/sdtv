FROM alpine:3.19

WORKDIR /app

# 安装Python和pip
RUN apk add --no-cache python3 py3-pip

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

EXPOSE 9002

CMD ["python3", "app.py"]