FROM node:lts
# Set working directory
WORKDIR /app/frontend

# install node modules
COPY ./package*.json ./
RUN npm install

# Copy all files from current directory to working dir in image
COPY . .

ENTRYPOINT [ "npm", "start"]