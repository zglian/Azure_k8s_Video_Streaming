# 使用官方的 Node.js 映像
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

CMD ["npm", "start"]