FROM node:20-alpine
WORKDIR /usr/src/app
COPY package.json package-lock.json* ./
RUN npm ci --only=production || npm install --production
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
