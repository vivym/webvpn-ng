# WebVPN NG

TCP over [BUAA WebVPN](https://d.buaa.edu.cn/). 把WebVPN转换成TCP协议，可以转发基于TCP的任意端口（例如：SSH，HTTPS）。

## 1. Requirements
Python >= 3.8

## 2. Install
```bash
pip install --upgrade webvpn-ng
```

## 3. Usage

### Login

使用BUAA统一认证账号密码登录WebVPN，个人token请私聊我获取。

```bash
wvpn login USERNAME
```

### Port Forwarding

例如，使用本地2222端口访问校内的10.251.0.24:22：

```bash
# terminal #1
webvpn forward --port 2222 --rhost 10.251.0.24

# terminal #2
ssh -p 2222 yangming@localhost

# terminal #3
scp -P 2222 yangming@localhost:/data/data.pth .
```

使用本地的8000端口访问校内的211.71.15.34:6000（Tensorboard）：

```bash
# terminal
webvpn forward --port 8000 --rhost 211.71.15.34 --rport 6000

# web browser
open http://localhost:8000
```
