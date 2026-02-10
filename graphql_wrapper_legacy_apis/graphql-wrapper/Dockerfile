FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
COPY tests ./tests
RUN npm run build
ENV PORT=4000
EXPOSE 4000
CMD ["node", "dist/index.js"]
