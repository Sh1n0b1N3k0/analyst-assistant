FROM node:18-alpine

WORKDIR /app

# Копирование package files
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование исходного кода
COPY . .

# Открыть порт
EXPOSE 3000

# Запуск dev сервера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

