FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# In production, we would build and serve with Nginx, 
# but for a "final prototype" dev mode with proxy is often fine or we can build it.
# Let's do a simple dev server for now or build it.
# Given it's a prototype, dev server is easier to iterate.

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
