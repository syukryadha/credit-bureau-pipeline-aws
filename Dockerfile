# Base image — AWS provides official Lambda base images
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all your code
COPY handler.py main.py ./
COPY config/ ./config/
COPY extract/ ./extract/
COPY transform/ ./transform/
COPY load/ ./load/

# Tell Lambda which function to run
CMD ["handler.lambda_handler"]