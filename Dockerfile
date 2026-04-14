FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY build/requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY pipeline/ ./pipeline/

CMD ["pipeline.handler.lambda_handler"]