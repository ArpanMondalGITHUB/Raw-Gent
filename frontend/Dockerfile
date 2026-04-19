FROM node:20-alpine AS build

WORKDIR /app

COPY package.json yarn.lock ./
RUN corepack enable && yarn install --frozen-lockfile

ARG VITE_API_URL=
ARG VITE_WS_URL=
ARG VITE_LOGIN_URL=
ARG VITE_GITHUB_APP_INSTALL_URL=

ENV VITE_API_URL=${VITE_API_URL} \
    VITE_WS_URL=${VITE_WS_URL} \
    VITE_LOGIN_URL=${VITE_LOGIN_URL} \
    VITE_GITHUB_APP_INSTALL_URL=${VITE_GITHUB_APP_INSTALL_URL}

COPY . .
RUN yarn build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
