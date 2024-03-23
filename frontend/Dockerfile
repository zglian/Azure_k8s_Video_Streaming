FROM node:latest
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npx update-browserslist-db@latest

CMD ["npm", "start"]