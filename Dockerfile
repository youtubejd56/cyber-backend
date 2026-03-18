# build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# runtime stage
FROM nginx:1.29-alpine

# install envsubst (gettext) for runtime template substitution
RUN apk add --no-cache gettext

COPY --from=build /app/dist /usr/share/nginx/html

# copy nginx template and startup script; they will be substituted at container start
COPY nginx/default.conf.template /etc/nginx/conf.d/default.conf.template
COPY nginx/start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

# run startup script which generates /etc/nginx/conf.d/default.conf then starts nginx
CMD ["/start.sh"]