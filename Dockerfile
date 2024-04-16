FROM python:3-alpine 

# Change App Dir 

WORKDIR /app

# COPY requirements to working Dir 

COPY . . 

# Install Packages 

RUN apk update 
RUN pip3 install flask flask_sqlalchemy

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
