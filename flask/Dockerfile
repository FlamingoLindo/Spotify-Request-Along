# Stage 1: Build CSS with Node.js
FROM node:alpine AS css-builder

WORKDIR /build
COPY static/src/input.css ./static/src/input.css
COPY static/src ./static/src

# Create a minimal package.json just for Tailwind
RUN echo '{"devDependencies":{"@tailwindcss/cli":"^4.2.1","tailwindcss":"^4.2.1"}}' > package.json && \
    npm install && \
    npx tailwindcss -i ./static/src/input.css -o ./static/dist/output.css

# Stage 2: Python application
FROM python:3.13.7-alpine

# upgrade pip
RUN pip install --upgrade pip

# get curl for healthchecks
RUN apk add curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot . .

# copy built CSS from stage 1
COPY --from=css-builder --chown=nonroot:nonroot /build/static/dist ./static/dist

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt

# define the port number the container should expose
EXPOSE 5000

CMD ["python", "app.py"]