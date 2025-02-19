# Создание chroot-окружения, сборка LuaJIT, OpenResty и создание deb-пакетов

## **1. Подготовка окружения**
Перед началом убедитесь, что в системе установлены необходимые инструменты:
```bash
sudo apt update
sudo apt install -y debootstrap qemu-user-static devscripts debhelper dh-make fakeroot build-essential
```

### **1.1. Создание chroot-окружения**
Создадим chroot-директорию для сборки:
```bash
sudo debootstrap --arch=amd64 --components=main,contrib,non-free stable chroot-env http://deb.debian.org/debian/
```
Настроим окружение:
```bash
sudo mount -t proc /proc chroot-env/proc
sudo mount --rbind /sys chroot-env/sys
sudo mount --rbind /dev chroot-env/dev
```
Зайдём в chroot:
```bash
sudo chroot chroot-env /bin/bash
```
Обновим пакеты и установим зависимости:
```bash
apt update
apt install -y build-essential libpcre3-dev libssl-dev zlib1g-dev curl git
```

---

## **2. Сборка LuaJIT (оригинальной версии)**
Скачаем исходники LuaJIT:
```bash
git clone https://luajit.org/git/luajit-2.0.git
cd luajit-2.0
make -j$(nproc)
make install PREFIX=/usr/local
```
Проверим, что LuaJIT работает:
```bash
luajit -v
```

---

## **3. Сборка OpenResty с модулем lua-resty-http**
Скачаем исходники OpenResty:
```bash
cd /root
wget https://openresty.org/download/openresty-1.21.4.1.tar.gz
tar -xzf openresty-1.21.4.1.tar.gz
cd openresty-1.21.4.1
```
Сконфигурируем и соберём OpenResty с поддержкой LuaJIT:
```bash
./configure --with-luajit --with-pcre --with-http_ssl_module
make -j$(nproc)
make install
```
Проверим версию:
```bash
/usr/local/openresty/bin/openresty -V
```
Установим lua-resty-http:
```bash
/usr/local/openresty/bin/opm get ledgetech/lua-resty-http
```

---

## **4. Создание deb-пакетов**

### **4.1. Создание deb-пакета для LuaJIT**
Создадим структуру:
```bash
mkdir -p luajit-deb/DEBIAN
mkdir -p luajit-deb/usr/local
cp -r /usr/local/bin /usr/local/lib /usr/local/include luajit-deb/usr/local/
```
Создадим `control`-файл:
```bash
nano luajit-deb/DEBIAN/control
```
Добавим:
```
Package: luajit
Version: 2.1.0-beta3
Section: libs
Priority: optional
Architecture: amd64
Maintainer: Your Name <your.email@example.com>
Description: LuaJIT 2.1.0-beta3
```
Соберём deb-пакет:
```bash
dpkg-deb --build luajit-deb
```

---

### **4.2. Создание deb-пакета для OpenResty**
Создадим структуру:
```bash
mkdir -p openresty-deb/DEBIAN
mkdir -p openresty-deb/usr/local/openresty
cp -r /usr/local/openresty/* openresty-deb/usr/local/openresty/
```
Создадим `control`-файл:
```bash
nano openresty-deb/DEBIAN/control
```
Добавим:
```
Package: openresty
Version: 1.21.4.1
Section: web
Priority: optional
Architecture: amd64
Maintainer: Your Name <your.email@example.com>
Depends: luajit
Description: OpenResty with lua-resty-http
```
Создадим postinst-скрипт:
```bash
nano openresty-deb/DEBIAN/postinst
```
Добавим:
```bash
#!/bin/bash
set -e
ln -s /usr/local/openresty/bin/openresty /usr/bin/openresty || true
ln -s /usr/local/openresty/bin/resty /usr/bin/resty || true
chmod +x /usr/bin/openresty
chmod +x /usr/bin/resty
```
Делаем исполняемым:
```bash
chmod +x openresty-deb/DEBIAN/postinst
```
Собираем deb-пакет:
```bash
dpkg-deb --build openresty-deb
```

---

## **5. Установка и тестирование**
Удаляем старый LuaJIT:
```bash
sudo dpkg -r luajit
```
Устанавливаем новые пакеты:
```bash
sudo dpkg -i luajit-deb.deb
sudo dpkg -i openresty-deb.deb
```
Проверяем:
```bash
luajit -v
openresty -V
ls -l /usr/local/openresty/site/lualib/resty/http.lua
```

Готово! 🎉 Теперь OpenResty с lua-resty-http собран и установлен. 🚀



# openresty--squid

Luarocks доступен в следующих сборках OpenResty:

LuaRocks is included in the alpine-fat, centos, and bionic variants. It is excluded from alpine because it generally requires a build system and we want to keep that variant lean.

Добавить в Dockerfile Openresty:
`RUN /usr/local/openresty/luajit/bin/luarocks install lua-resty-http`

