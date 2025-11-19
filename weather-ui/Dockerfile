FROM node:20-alpine AS build
WORKDIR /app
COPY weather-ui/package.json weather-ui/package-lock.json ./
COPY weather-ui/ .
RUN npm ci && npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY weather-ui/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
