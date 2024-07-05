# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:20 as build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

# Copy the built app from the previous stage
COPY --from=build-stage /app/dist/ /usr/share/nginx/html

# Copy Nginx configuration template
COPY ./nginx.conf /etc/nginx/nginx.conf.template
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

# Expose the port nginx is reachable on
EXPOSE 8080

# Use `envsubst` to replace the $PORT variable placeholder with the actual PORT environment variable
CMD /bin/bash -c "envsubst '$$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"
