# # frontend/Dockerfile
# FROM node:14-alpine

# # Set working directory
# WORKDIR /app

# # Copy package.json and package-lock.json
# COPY package.json ./

# # Install dependencies
# RUN npm install

# # Copy the rest of the application
# COPY . .

# # Build the app
# RUN npm run build

# # Install serve to serve the build
# RUN npm install -g serve

# # Expose port 3000
# EXPOSE 3000

# # Start the app
# CMD ["serve", "-s", "build", "-l", "3000"]


# Use Node.js version 14-alpine
FROM node:14-alpine

# Set working directory inside the container
WORKDIR /app

# Copy only package.json and package-lock.json first (to cache dependencies)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React application
RUN npm run build

# Install serve globally to serve the React app
RUN npm install -g serve

# Expose port 3000 for the React app
EXPOSE 3000

# Serve the build directory on port 3000
CMD ["serve", "-s", "build", "-l", "3000"]
