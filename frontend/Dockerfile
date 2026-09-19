# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the React/Vite app with correct API URL
RUN VITE_API_BASE_URL=/api/v1 npm run build

# Serve stage
FROM nginx:alpine

# Copy built assets from build stage to nginx serve directory
COPY --from=build /app/dist /usr/share/nginx/html

# Use custom nginx config with API proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
