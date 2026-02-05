FROM alpine:3.19

# 使用国内 Alpine 镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt .

# 使用国内 PyPI 镜像
RUN pip3 install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

COPY app.py .

EXPOSE 9002

CMD ["python3", "app.py"]