FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
RUN npm run build
ENV PORT=4001
EXPOSE 4001
CMD ["node", "dist/server.js"]
