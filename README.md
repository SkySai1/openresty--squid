# openresty--squid

Luarocks доступен в следующих сборках OpenResty:

LuaRocks is included in the alpine-fat, centos, and bionic variants. It is excluded from alpine because it generally requires a build system and we want to keep that variant lean.

Добавить в Dockerfile Openresty:
`RUN /usr/local/openresty/luajit/bin/luarocks install lua-resty-http`

