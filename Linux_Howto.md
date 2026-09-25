```
git clone https://github.com/URT19/XRAY-Config-Benchmark.git
cd XRAY-Config-Benchmark
```

```
apt update
apt install -y python3-venv python3-full
```


```
python3 -m venv venv
source venv/bin/activate
```

```
pip install -r requirements.txt

```


### 💡 نکته مهم: هر بار که از سیستم خارج و دوباره وارد می‌شوید، باید قبل از اجرای پروژه، دوباره محیط مجازی را فعال کنید:

```
cd ~/XRAY-Config-Benchmark
source venv/bin/activate
```

----


### Update Resolve?


```
echo "nameserver 1.1.1.1" >  /etc/resolv.conf
```


### Run Script?


```
python3.12 cf_xray_benchmark.py
```

----

### Add Xray Links?

```
nano links.txt
```

### Add Cloudflare Whitelist IP?

```
nano cfip.txt
```

---

### Change Script Config?

```
nano config.json
```

--


### Run Test and Script?


```
python3.12 cf_xray_benchmark.py
```


