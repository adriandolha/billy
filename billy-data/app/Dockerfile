FROM public.ecr.aws/lambda/python:3.9
COPY --from=openjdk:11 /usr/local/openjdk-11 /usr/local/openjdk-11
ENV JAVA_HOME /usr/local/openjdk-11
ENV PATH $PATH:$JAVA_HOME/bin
RUN java --version
RUN python --version
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt
RUN echo ${LAMBDA_TASK_ROOT}
COPY . ${LAMBDA_TASK_ROOT}/
CMD ["app.lambda_handler"]