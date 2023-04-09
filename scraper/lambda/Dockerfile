FROM amazon/aws-lambda-python:latest

COPY lambda_function.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["lambda_function.lambda_handler"]